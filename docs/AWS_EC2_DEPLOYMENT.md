# AWS EC2 Deployment Guide - Commerce Platform

## Overview
This guide deploys both Identity and Product services on a single AWS EC2 instance with:
- **1 MySQL Container** (shared database for both services)
- **1 Redis Container** (shared cache for both services)
- **2 Django Services** (Identity Service + Product Service)

---

## Prerequisites

### AWS Requirements
- EC2 Instance (Ubuntu 22.04 LTS recommended)
- Instance Type: **t3.medium** or higher (at least 2GB RAM)
- Security Groups configured with ports:
  - Port 22 (SSH)
  - Port 8000 (Identity Service)
  - Port 8002 (Product Service)
  - Port 3306 (MySQL - internal only, not exposed to public)
  - Port 6379 (Redis - internal only, not exposed to public)

### Local Environment
- Docker and Docker Compose installed locally for building images

---

## Step 1: Prepare EC2 Instance

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

---

## Step 2: Clone Repository on EC2

```bash
cd /home/ubuntu

# Clone the repository
git clone https://github.com/your-org/commerce-platform.git
cd commerce-platform

# Create .env file for production
nano .env
```

### Sample .env file:
```env
# MySQL Configuration
MYSQL_ROOT_PASSWORD=your-secure-password-here
MYSQL_USER=commerce_user
DB_USER=commerce_user

# Identity Service
IDENTITY_DB_NAME=commerce_identity_db
IDENTITY_SECRET_KEY=your-identity-secret-key-here

# Product Service
PRODUCT_DB_NAME=commerce_product_db
PRODUCT_SECRET_KEY=your-product-secret-key-here

# Common Configuration
ALLOWED_HOSTS=your-ec2-ip,your-domain.com,www.your-domain.com
ENVIRONMENT=production
```

---

## Step 3: Build and Push Docker Images (Optional - Only if building on EC2)

If you have sufficient resources on EC2:

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Or build locally and push to Docker Hub/ECR, then pull on EC2
# docker-compose -f docker-compose.prod.yml pull
```

---

## Step 4: Deploy Services

```bash
# Start all services (MySQL, Redis, Identity Service, Product Service)
docker-compose -f docker-compose.prod.yml up -d

# Verify all containers are running
docker-compose -f docker-compose.prod.yml ps

# Expected output:
# NAME                      STATUS              PORTS
# commerce-mysql-prod       Up (healthy)        0.0.0.0:3306->3306/tcp
# commerce-redis-prod       Up (healthy)        0.0.0.0:6379->6379/tcp
# identity-service-prod     Up                  0.0.0.0:8000->8000/tcp
# product-service-prod      Up                  0.0.0.0:8002->8000/tcp
```

---

## Step 5: Verify Deployment

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check specific service logs
docker-compose -f docker-compose.prod.yml logs identity-service
docker-compose -f docker-compose.prod.yml logs product-service

# Test Identity Service
curl http://your-ec2-ip:8000/api/health/

# Test Product Service
curl http://your-ec2-ip:8002/api/products/
```

---

## Step 6: Setup Nginx Reverse Proxy (Recommended)

Create `/etc/nginx/sites-available/commerce-platform`:

```nginx
upstream identity_service {
    server 127.0.0.1:8000;
}

upstream product_service {
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 20M;

    location /identity/ {
        proxy_pass http://identity_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /products/ {
        proxy_pass http://product_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        return 404;
    }
}
```

Enable and test Nginx:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/commerce-platform /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Step 7: Setup SSL with Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is enabled by default
sudo systemctl enable certbot.timer
```

---

## Step 8: Setup Systemd Service for Auto-Start

Create `/etc/systemd/system/commerce-docker.service`:

```ini
[Unit]
Description=Commerce Platform Docker Services
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/home/ubuntu/commerce-platform
RemainAfterExit=yes
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable auto-start:

```bash
sudo systemctl enable commerce-docker.service
sudo systemctl start commerce-docker.service

# Check status
sudo systemctl status commerce-docker.service
```

---

## Step 9: Setup Database Backups

Create backup script `/home/ubuntu/backup-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER="commerce-mysql-prod"

mkdir -p $BACKUP_DIR

# Backup both databases
docker exec $CONTAINER mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} \
  --single-transaction --quick --lock-tables=false \
  --all-databases > $BACKUP_DIR/commerce_backup_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "commerce_backup_*.sql" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/commerce_backup_$DATE.sql"
```

Add to crontab:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/ubuntu/backup-db.sh >> /home/ubuntu/backups/backup.log 2>&1
```

---

## Monitoring & Management

### View Container Status
```bash
docker-compose -f docker-compose.prod.yml ps

# View detailed logs
docker-compose -f docker-compose.prod.yml logs --follow

# View logs for specific container
docker-compose -f docker-compose.prod.yml logs identity-service
docker-compose -f docker-compose.prod.yml logs product-service
```

### Restart Services
```bash
# Restart specific service
docker-compose -f docker-compose.prod.yml restart identity-service
docker-compose -f docker-compose.prod.yml restart product-service

# Restart all services
docker-compose -f docker-compose.prod.yml restart
```

### Database Access
```bash
# Connect to MySQL
docker exec -it commerce-mysql-prod mysql -uroot -p

# Inside MySQL shell:
# SHOW DATABASES;
# USE commerce_identity_db;
# SHOW TABLES;
```

### Redis Access
```bash
# Connect to Redis CLI
docker exec -it commerce-redis-prod redis-cli

# Inside Redis CLI:
# PING
# KEYS *
# INFO
```

---

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Check memory
free -h

# Rebuild containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Database Connection Issues
```bash
# Check if database is healthy
docker exec commerce-mysql-prod mysqladmin -uroot -p${MYSQL_ROOT_PASSWORD} ping

# Check logs
docker-compose -f docker-compose.prod.yml logs db
```

### Port Already in Use
```bash
# Find what's using the port
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :8002

# Kill the process if needed
sudo kill -9 <PID>

# Or change ports in docker-compose.prod.yml
```

### Out of Disk Space
```bash
# Check disk usage
docker system df

# Clean up unused images/containers/volumes
docker system prune -a --volumes
```

---

## Environment Variables Reference

| Variable | Service | Example | Notes |
|----------|---------|---------|-------|
| `MYSQL_ROOT_PASSWORD` | Global | `SecurePass123!` | Root password for MySQL |
| `MYSQL_USER` | Global | `commerce_user` | MySQL user (optional) |
| `IDENTITY_DB_NAME` | Identity | `commerce_identity_db` | Database name for Identity Service |
| `PRODUCT_DB_NAME` | Product | `commerce_product_db` | Database name for Product Service |
| `IDENTITY_SECRET_KEY` | Identity | `your-secret-key` | Django SECRET_KEY for Identity |
| `PRODUCT_SECRET_KEY` | Product | `your-secret-key` | Django SECRET_KEY for Product |
| `ALLOWED_HOSTS` | Both | `ip,domain.com` | Comma-separated allowed hosts |
| `ENVIRONMENT` | Both | `docker` | Set to 'docker' for container env |

---

## Scale Resources

If you need better performance:

### Increase Gunicorn Workers
Edit `docker-compose.prod.yml` and update the command:
```bash
gunicorn product_service.wsgi:application --bind 0.0.0.0:8000 --workers 8 --timeout 120
```

### Increase MySQL Buffer Pool
Add to MySQL environment in `docker-compose.prod.yml`:
```yaml
environment:
  MYSQL_INNODB_BUFFER_POOL_SIZE: 1G
```

### Use RDS for MySQL (Recommended for Production)
Replace the MySQL container with AWS RDS and update connection strings:
```yaml
environment:
  DB_HOST: your-rds-endpoint.rds.amazonaws.com
  DB_PORT: 3306
```

---

## Security Recommendations

1. **Change Default Passwords**: Update all default credentials in `.env`
2. **Enable SSL/TLS**: Use Let's Encrypt certificate (see Step 7)
3. **Restrict Security Groups**: Only allow necessary ports to specific IPs
4. **Enable CloudWatch Logs**: Monitor container logs in AWS CloudWatch
5. **Setup IAM Roles**: Use IAM roles for EC2 instead of storing AWS credentials
6. **Regular Backups**: Implement automated database backups (see Step 9)
7. **Keep Images Updated**: Regularly update base images and dependencies

---

## Rollback Procedure

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restore database backup
docker exec -i commerce-mysql-prod mysql -uroot -p${MYSQL_ROOT_PASSWORD} < backup_file.sql

# Start services again
docker-compose -f docker-compose.prod.yml up -d
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## Support & Issues

For issues or questions:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Review this guide's Troubleshooting section
3. Contact the development team with error logs

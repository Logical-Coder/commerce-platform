# Unified AWS EC2 Deployment - Quick Reference

## What's New ✨

Your commerce platform is now configured for unified AWS EC2 deployment with:

### Architecture
```
AWS EC2 Instance
├── Single MySQL Container (Port 3306)
│   ├── commerce_identity_db
│   └── commerce_product_db
├── Single Redis Container (Port 6379)
├── Identity Service (Port 8000)
└── Product Service (Port 8002)
```

### Benefits
- **Single Database**: Both services share one MySQL container
- **Single Cache Layer**: Both services share one Redis container
- **Resource Efficient**: Reduced memory and CPU consumption
- **Easy Maintenance**: One place to manage backups and updates
- **Cost Effective**: Fewer containers = lower AWS EC2 costs

---

## Files Created/Modified

| File | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Main deployment configuration for AWS EC2 |
| `docs/AWS_EC2_DEPLOYMENT.md` | Comprehensive deployment guide |
| `.env.production.example` | Environment variables template |
| `scripts/deploy-to-aws-ec2.sh` | Automated deployment script |
| `docker/my_sql/init/01-create-databases.sql` | Updated with product database |

---

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# On your AWS EC2 instance (as ubuntu user with sudo access)
sudo bash /tmp/deploy-to-aws-ec2.sh
```

This script:
- ✓ Installs Docker and Docker Compose
- ✓ Clones your repository
- ✓ Creates `.env` file with configuration
- ✓ Starts all services
- ✓ Runs migrations
- ✓ Sets up automated backups
- ✓ Configures systemd for auto-start

### Option 2: Manual Deployment

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Clone repository
git clone https://github.com/your-org/commerce-platform.git
cd commerce-platform

# Copy and edit environment file
cp .env.production.example .env
nano .env

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
```

---

## Environment Configuration

### Create `.env` File

```bash
# Copy the example
cp .env.production.example .env

# Edit with your values
nano .env
```

### Key Variables

```env
# MySQL
MYSQL_ROOT_PASSWORD=your-secure-password

# Identity Service
IDENTITY_DB_NAME=commerce_identity_db
IDENTITY_SECRET_KEY=your-secret-key

# Product Service
PRODUCT_DB_NAME=commerce_product_db
PRODUCT_SECRET_KEY=your-secret-key

# Common
ALLOWED_HOSTS=your-ec2-ip,your-domain.com
ENVIRONMENT=production
```

### Generate Secret Keys

```bash
# Python method
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# OpenSSL method
openssl rand -hex 32
```

---

## Service URLs

After deployment:
- **Identity Service**: `http://your-ec2-ip:8000`
- **Product Service**: `http://your-ec2-ip:8002`
- **MySQL**: `your-ec2-ip:3306`
- **Redis**: `your-ec2-ip:6379`

---

## Common Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs identity-service
docker-compose -f docker-compose.prod.yml logs product-service
```

### Restart Services
```bash
# All services
docker-compose -f docker-compose.prod.yml restart

# Specific service
docker-compose -f docker-compose.prod.yml restart identity-service
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Access Database
```bash
# MySQL
docker exec -it commerce-mysql-prod mysql -uroot -p

# Redis
docker exec -it commerce-redis-prod redis-cli
```

### Run Migrations
```bash
# Identity Service
docker-compose -f docker-compose.prod.yml exec identity-service python manage.py migrate

# Product Service
docker-compose -f docker-compose.prod.yml exec product-service python manage.py migrate
```

### Create Superuser
```bash
# Identity Service
docker-compose -f docker-compose.prod.yml exec identity-service python manage.py createsuperuser

# Product Service
docker-compose -f docker-compose.prod.yml exec product-service python manage.py createsuperuser
```

### Manual Backup
```bash
docker exec commerce-mysql-prod mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} \
  --all-databases > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## AWS Security Groups Configuration

Add inbound rules:

| Type | Protocol | Port Range | Source |
|------|----------|-----------|--------|
| SSH | TCP | 22 | Your IP (0.0.0.0/0 for testing only) |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 (or specific IPs) |
| Custom TCP | TCP | 8002 | 0.0.0.0/0 (or specific IPs) |

⚠️ **Note**: MySQL (3306) and Redis (6379) should NOT be exposed publicly. Keep them internal only.

---

## Production Recommendations

### 1. Setup Nginx Reverse Proxy
```bash
sudo apt-get install -y nginx
# Configure as shown in AWS_EC2_DEPLOYMENT.md
```

### 2. Setup SSL Certificate
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Configure Automated Backups
```bash
# Add to crontab
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * /home/ubuntu/backup-db.sh >> /home/ubuntu/backups/backup.log 2>&1
```

### 4. Setup Monitoring
- Monitor disk space: `df -h`
- Monitor memory: `free -h`
- Monitor containers: `docker stats`
- Check logs regularly: `docker-compose logs`

### 5. Enable Auto-Start
```bash
# If using systemd service (created by deploy script)
sudo systemctl enable commerce-docker.service
sudo systemctl start commerce-docker.service
```

---

## Troubleshooting

### Services Won't Start
```bash
# Check errors
docker-compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Restart Docker
sudo systemctl restart docker
```

### Database Connection Failed
```bash
# Check if MySQL is healthy
docker exec commerce-mysql-prod mysqladmin -uroot -p${MYSQL_ROOT_PASSWORD} ping

# Check MySQL logs
docker-compose logs db
```

### Port Already in Use
```bash
# Find what's using the port
sudo lsof -i :8000
sudo lsof -i :8002

# Kill the process
sudo kill -9 <PID>
```

### Out of Memory
```bash
# Check current usage
docker stats

# Reduce workers in docker-compose.prod.yml
# Change: gunicorn ... --workers 4
# To:     gunicorn ... --workers 2
```

---

## Updating Services

### Pull Latest Code
```bash
cd /home/ubuntu/commerce-platform
git pull origin main
```

### Rebuild Images
```bash
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Rollback Previous Version
```bash
git revert HEAD
git push origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

## Database Backup/Restore

### Backup
```bash
docker exec commerce-mysql-prod mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} \
  --all-databases > commerce_backup.sql
```

### Restore
```bash
docker exec -i commerce-mysql-prod mysql -uroot -p${MYSQL_ROOT_PASSWORD} < commerce_backup.sql
```

---

## Advanced Configuration

### Using AWS RDS Instead of Container
Replace MySQL container with RDS endpoint:

Edit `.env`:
```env
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=3306
```

Update `docker-compose.prod.yml`: Remove or comment out the `db` service.

### Using AWS ElastiCache for Redis
Edit `.env`:
```env
REDIS_HOST=your-elasticache-endpoint.cache.amazonaws.com
REDIS_PORT=6379
```

Update `docker-compose.prod.yml`: Remove or comment out the `redis` service.

---

## Performance Tuning

### Increase Workers
```yaml
# In docker-compose.prod.yml
command: gunicorn ... --workers 8  # Increase from 4
```

### Increase MySQL Buffer Pool
```yaml
environment:
  MYSQL_INNODB_BUFFER_POOL_SIZE: 2G  # Increase from default
```

### Enable Redis Persistence
```yaml
# Redis is already configured with appendonly yes
# For more options, see docs/AWS_EC2_DEPLOYMENT.md
```

---

## Support & Documentation

- **Full Guide**: See `docs/AWS_EC2_DEPLOYMENT.md`
- **Environment Template**: See `.env.production.example`
- **Auto-Deploy Script**: See `scripts/deploy-to-aws-ec2.sh`
- **Docker Docs**: https://docs.docker.com/
- **AWS EC2 Docs**: https://docs.aws.amazon.com/ec2/

---

## Checklist for Production

- [ ] Update all passwords in `.env`
- [ ] Configure security groups in AWS
- [ ] Setup Nginx reverse proxy
- [ ] Enable SSL certificate with Let's Encrypt
- [ ] Configure automated backups
- [ ] Test all endpoints
- [ ] Monitor logs and resource usage
- [ ] Setup CloudWatch monitoring (optional)
- [ ] Document any custom configurations
- [ ] Create runbooks for common operations

---

## Emergency Procedures

### Emergency Restart
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Emergency Stop
```bash
docker-compose -f docker-compose.prod.yml down
```

### Emergency Recovery
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore from backup
docker exec -i commerce-mysql-prod mysql -uroot -p${MYSQL_ROOT_PASSWORD} < backup.sql

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

---

## Next Steps

1. ✅ Read the full guide: `docs/AWS_EC2_DEPLOYMENT.md`
2. ✅ Prepare your AWS EC2 instance
3. ✅ Configure security groups
4. ✅ Run the deployment script
5. ✅ Test the services
6. ✅ Setup monitoring and backups
7. ✅ Configure domain and SSL
8. ✅ Deploy to production!

---

**Questions?** Check the Troubleshooting section or review `docs/AWS_EC2_DEPLOYMENT.md`

Good luck! 🚀

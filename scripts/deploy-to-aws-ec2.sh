#!/bin/bash

# Commerce Platform - AWS EC2 Auto-Deployment Script
# This script automates the setup of Docker, pulling the repository, 
# and deploying both services with shared MySQL and Redis containers

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/your-org/commerce-platform.git"
APP_DIR="/home/ubuntu/commerce-platform"
BACKUP_DIR="/home/ubuntu/backups"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Commerce Platform - AWS EC2 Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "${YELLOW}[*] $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

# Function to print error and exit
print_error() {
    echo -e "${RED}[✗] $1${NC}"
    exit 1
}

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
fi

# ================================
# Step 1: Update System
# ================================
print_section "Step 1: Updating system packages"
apt-get update
apt-get upgrade -y
print_success "System packages updated"

# ================================
# Step 2: Install Docker
# ================================
print_section "Step 2: Installing Docker"
if command -v docker &> /dev/null; then
    print_success "Docker is already installed"
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_success "Docker installed successfully"
fi

# ================================
# Step 3: Install Docker Compose
# ================================
print_section "Step 3: Installing Docker Compose"
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
print_success "Docker Compose installed successfully (version: $COMPOSE_VERSION)"

# ================================
# Step 4: Add ubuntu user to docker group
# ================================
print_section "Step 4: Configuring Docker permissions"
usermod -aG docker ubuntu
print_success "Ubuntu user added to docker group"

# ================================
# Step 5: Clone Repository
# ================================
print_section "Step 5: Cloning repository"
if [ -d "$APP_DIR" ]; then
    print_section "Repository already exists. Updating..."
    cd "$APP_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"
print_success "Repository ready at $APP_DIR"

# ================================
# Step 6: Create .env file
# ================================
print_section "Step 6: Setting up environment configuration"
if [ ! -f "$APP_DIR/.env" ]; then
    echo ""
    echo -e "${YELLOW}Please provide the following information:${NC}"
    
    read -p "Enter MySQL Root Password: " MYSQL_ROOT_PASSWORD
    read -p "Enter Identity Service Secret Key (or press Enter to generate): " IDENTITY_SECRET_KEY
    read -p "Enter Product Service Secret Key (or press Enter to generate): " PRODUCT_SECRET_KEY
    read -p "Enter EC2 Instance Public IP or Domain: " ALLOWED_HOSTS
    
    # Generate secret keys if not provided
    if [ -z "$IDENTITY_SECRET_KEY" ]; then
        IDENTITY_SECRET_KEY=$(openssl rand -hex 32)
    fi
    if [ -z "$PRODUCT_SECRET_KEY" ]; then
        PRODUCT_SECRET_KEY=$(openssl rand -hex 32)
    fi
    
    # Create .env file
    cat > "$APP_DIR/.env" << EOF
# MySQL Configuration
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MYSQL_USER=commerce_user
DB_USER=commerce_user

# Identity Service Configuration
IDENTITY_DB_NAME=commerce_identity_db
IDENTITY_SECRET_KEY=$IDENTITY_SECRET_KEY

# Product Service Configuration
PRODUCT_DB_NAME=commerce_product_db
PRODUCT_SECRET_KEY=$PRODUCT_SECRET_KEY

# Common Configuration
ENVIRONMENT=production
ALLOWED_HOSTS=$ALLOWED_HOSTS
DEBUG=False
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
EOF
    
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# ================================
# Step 7: Create backup directory
# ================================
print_section "Step 7: Setting up backup directory"
mkdir -p "$BACKUP_DIR"
chown ubuntu:ubuntu "$BACKUP_DIR"
print_success "Backup directory created at $BACKUP_DIR"

# ================================
# Step 8: Pull Docker images
# ================================
print_section "Step 8: Pulling Docker images"
cd "$APP_DIR"
docker-compose -f docker-compose.prod.yml pull || print_error "Failed to pull images"
print_success "Docker images pulled successfully"

# ================================
# Step 9: Build and start services
# ================================
print_section "Step 9: Building and starting services"
docker-compose -f docker-compose.prod.yml up -d || print_error "Failed to start services"
print_success "Services started successfully"

# ================================
# Step 10: Wait for services to be ready
# ================================
print_section "Step 10: Waiting for services to be ready"
sleep 10

# ================================
# Step 11: Run migrations
# ================================
print_section "Step 11: Running database migrations"
docker-compose -f docker-compose.prod.yml exec -T identity-service python manage.py migrate || echo "Identity service migrations may have already run"
docker-compose -f docker-compose.prod.yml exec -T product-service python manage.py migrate || echo "Product service migrations may have already run"
print_success "Migrations completed"

# ================================
# Step 12: Create backup script
# ================================
print_section "Step 12: Setting up automated backup script"
cat > /home/ubuntu/backup-db.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +\%Y\%m\%d_\%H\%M\%S)
CONTAINER="commerce-mysql-prod"
MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}"

mkdir -p $BACKUP_DIR

docker exec $CONTAINER mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} \
  --single-transaction --quick --lock-tables=false \
  --all-databases > $BACKUP_DIR/commerce_backup_$DATE.sql 2>/dev/null

find $BACKUP_DIR -name "commerce_backup_*.sql" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/commerce_backup_$DATE.sql"
EOF

chmod +x /home/ubuntu/backup-db.sh
chown ubuntu:ubuntu /home/ubuntu/backup-db.sh
print_success "Backup script created"

# ================================
# Step 13: Setup Systemd service (optional)
# ================================
print_section "Step 13: Setting up Systemd service for auto-start"
cat > /etc/systemd/system/commerce-docker.service << EOF
[Unit]
Description=Commerce Platform Docker Services
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=$APP_DIR
RemainAfterExit=yes
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable commerce-docker.service
print_success "Systemd service configured for auto-start"

# ================================
# Step 14: Display Summary
# ================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Service Status:${NC}"
docker-compose -f "$APP_DIR/docker-compose.prod.yml" ps
echo ""
echo -e "${YELLOW}Important Information:${NC}"
echo "  App Directory: $APP_DIR"
echo "  Backup Directory: $BACKUP_DIR"
echo "  Identity Service: http://$(hostname -I | awk '{print $1}'):8000"
echo "  Product Service: http://$(hostname -I | awk '{print $1}'):8002"
echo "  MySQL: $(hostname -I | awk '{print $1}'):3306"
echo "  Redis: $(hostname -I | awk '{print $1}'):6379"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs: docker-compose -f $APP_DIR/docker-compose.prod.yml logs -f"
echo "  Restart services: docker-compose -f $APP_DIR/docker-compose.prod.yml restart"
echo "  Manual backup: /home/ubuntu/backup-db.sh"
echo "  Service status: sudo systemctl status commerce-docker.service"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Configure Nginx reverse proxy (optional but recommended)"
echo "  2. Setup SSL certificate with Let's Encrypt"
echo "  3. Configure automated backups in crontab"
echo "  4. Test services: curl http://$(hostname -I | awk '{print $1}'):8000/api/health/"
echo ""
echo -e "${GREEN}For detailed information, see docs/AWS_EC2_DEPLOYMENT.md${NC}"

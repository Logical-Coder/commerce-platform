# 🛒 Commerce Platform (Microservices Architecture)

A scalable, production-oriented backend system designed using **microservices architecture**.  
This repository currently contains the **Identity Service**, responsible for authentication and authorization.

---

## 🚀 Overview

The **Commerce Platform** is designed to support large-scale applications with modular services such as:

- Identity Service (✅ Implemented)
- Product Service (Planned)
- Order Service (Planned)
- Payment Service (Planned)

Each service is independently deployable and follows clean architecture principles.

---

## 🔐 Identity Service

The **Identity Service** handles:

- User registration
- User login
- JWT-based authentication
- Role-based access (extendable)
- Secure API access

---

## 🏗️ Architecture

```text
Client
   ↓
API Layer (Django REST Framework)
   ↓
Service Layer (Business Logic)
   ↓
Repository Layer (Database Access)
   ↓
Database (MySQL)


🧠 Design Principles
SOLID Principles
Separation of Concerns
Clean Architecture (Services, Repositories, Serializers)
Environment-based configuration
Microservices-ready structure
🧰 Tech Stack
Layer	Technology
Backend	Python, Django, Django REST Framework
Database	MySQL
Cache	Redis
Container	Docker, Docker Compose
CI/CD	GitHub Actions
Auth	JWT
Testing	Django Test Framework, Coverage
Code Quality	Flake8, Black
⚙️ Features
REST APIs for authentication
JWT-based secure authentication
MySQL integration
Redis integration
Dockerized environment
CI/CD pipeline with GitHub Actions
80%+ test coverage
Linting and formatting enforcement
🐳 Running Locally (Docker)
docker compose up --build

Access:

http://localhost:8000
🧪 Running Tests
coverage run manage.py test apps.accounts.tests
coverage report -m
🔄 CI/CD Pipeline

This project uses GitHub Actions for automation.

Pipeline Steps:
Install dependencies
Start MySQL & Redis
Run migrations
Execute tests
Check code coverage
Run Flake8 (linting)
Run Black (format check)
Build Docker image
Push image to GitHub Container Registry (GHCR)
📦 Docker Image

Image is published to:

ghcr.io/<your-username>/identity-service:latest
📊 Code Quality
Coverage: 80%+
Linting: Flake8
Formatting: Black
📁 Project Structure
commerce-platform/
│
├── identity-service/
│   ├── apps/
│   │   └── accounts/
│   │       ├── models.py
│   │       ├── views.py
│   │       ├── services.py
│   │       ├── repositories.py
│   │       ├── serializers.py
│   │       └── tests/
│   │
│   ├── manage.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── .github/
    └── workflows/
        └── ci-cd.yml
🔮 Future Enhancements
API Gateway integration
Role-Based Access Control (RBAC)
Refresh Token & Logout handling
Rate limiting with Redis
Service-to-service communication
Kubernetes deployment
Observability (logging, monitoring)
🧑‍💻 Author

Praveen Acharya
Backend Developer (Python)
Bangalore, India

GitHub: https://github.com/Logical-Coder

⭐ Why This Project?

This project demonstrates:

Real-world backend development practices
Microservices architecture thinking
CI/CD pipeline implementation
Docker-based deployment
Test-driven development approach

---

---

## 🚀 AWS EC2 Deployment (Unified Architecture)

The platform now supports unified deployment on AWS EC2 with a single MySQL and Redis container for both services.

### Deployment Architecture

```
AWS EC2 Instance (Ubuntu 22.04 LTS)
├── Single MySQL 8.4 Container
│   ├── commerce_identity_db
│   └── commerce_product_db
├── Single Redis 7 Container
├── Identity Service (Port 8000)
└── Product Service (Port 8002)
```

### Quick Start (Automated)

```bash
# Download and run the deployment script
sudo bash /tmp/deploy-to-aws-ec2.sh
```

The script will automatically:
- Install Docker and Docker Compose
- Clone the repository
- Create environment configuration
- Start all services
- Run migrations
- Setup automated backups
- Configure systemd for auto-start

### Manual Deployment

```bash
# 1. SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Clone repository
git clone https://github.com/your-org/commerce-platform.git
cd commerce-platform

# 3. Create environment file
cp .env.production.example .env
nano .env  # Edit with your values

# 4. Deploy services
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### Access Services After Deployment

- **Identity Service**: `http://your-ec2-ip:8000`
- **Product Service**: `http://your-ec2-ip:8002`
- **MySQL**: `your-ec2-ip:3306`
- **Redis**: `your-ec2-ip:6379`

### Important Files

| File | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Production deployment configuration |
| `docker-compose.dev.yml` | Local development with unified setup |
| `docs/AWS_EC2_DEPLOYMENT.md` | Comprehensive deployment guide |
| `docs/QUICK_REFERENCE_AWS_EC2.md` | Quick reference and common commands |
| `scripts/deploy-to-aws-ec2.sh` | Automated deployment script |
| `.env.production.example` | Environment variables template |

### Documentation

- 📖 **Full Deployment Guide**: See [docs/AWS_EC2_DEPLOYMENT.md](docs/AWS_EC2_DEPLOYMENT.md)
- ⚡ **Quick Reference**: See [docs/QUICK_REFERENCE_AWS_EC2.md](docs/QUICK_REFERENCE_AWS_EC2.md)

### Common Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Access MySQL
docker exec -it commerce-mysql-prod mysql -uroot -p

# Access Redis
docker exec -it commerce-redis-prod redis-cli

# Create backup
docker exec commerce-mysql-prod mysqldump -uroot -p${MYSQL_ROOT_PASSWORD} --all-databases > backup.sql
```

### Local Development with Unified Setup

Test the unified architecture locally before deploying:

```bash
# Start services locally (same setup as production)
docker-compose -f docker-compose.dev.yml up -d

# Access services
# Identity Service: http://localhost:8000
# Product Service: http://localhost:8002

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Production Recommendations

1. ✅ Setup Nginx reverse proxy
2. ✅ Enable SSL with Let's Encrypt
3. ✅ Configure automated backups
4. ✅ Monitor resource usage
5. ✅ Enable CloudWatch monitoring
6. ✅ Setup auto-scaling policies

See [docs/AWS_EC2_DEPLOYMENT.md](docs/AWS_EC2_DEPLOYMENT.md) for detailed instructions.

---

# 🔥 Optional (Add Badge at top)

Add this at the top:

```markdown
![CI](https://github.com/Logical-Coder/commerce-platform/actions/workflows/ci-cd.yml/badge.svg)
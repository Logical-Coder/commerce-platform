# Pre-Deployment Checklist

Before deploying to AWS EC2, verify the following:

## ✅ Local Environment Setup

- [ ] Docker is installed locally
- [ ] Docker Compose is installed locally
- [ ] Git is configured
- [ ] Repository is cloned

## ✅ AWS EC2 Preparation

- [ ] EC2 instance created (Ubuntu 22.04 LTS, t3.medium or larger)
- [ ] Elastic IP assigned (optional but recommended)
- [ ] Security groups configured with appropriate ports:
  - [ ] Port 22 (SSH)
  - [ ] Port 80 (HTTP)
  - [ ] Port 443 (HTTPS)
  - [ ] Port 8000 (Identity Service)
  - [ ] Port 8002 (Product Service)
- [ ] SSH key pair downloaded and stored securely
- [ ] Key pair permissions set correctly (`chmod 400 key.pem`)

## ✅ Code Verification

- [ ] `docker-compose.prod.yml` exists at repository root
- [ ] `docker-compose.dev.yml` exists at repository root
- [ ] `docker/my_sql/init/01-create-databases.sql` includes all databases
- [ ] Both services have Dockerfiles configured
- [ ] Both services have `scripts/wait_for_db.sh` script
- [ ] Identity service database settings use environment variables
- [ ] Product service database settings use environment variables

## ✅ Database Configuration

- [ ] Both services use `DB_HOST` environment variable
- [ ] Both services use `DB_PORT` environment variable  
- [ ] Both services use `DB_NAME` environment variable
- [ ] Both services use `DB_USER` environment variable
- [ ] Both services use `DB_PASSWORD` environment variable
- [ ] MySQL init script creates both databases:
  - [ ] commerce_identity_db
  - [ ] commerce_product_db

## ✅ Redis Configuration

- [ ] Redis container is defined in docker-compose.prod.yml
- [ ] Both services connect to same Redis host
- [ ] Redis persistence is enabled (`appendonly yes`)

## ✅ Environment Configuration

- [ ] `.env.production.example` file exists
- [ ] All required environment variables documented
- [ ] Secure password generation method documented
- [ ] ALLOWED_HOSTS configuration documented

## ✅ Documentation

- [ ] `docs/AWS_EC2_DEPLOYMENT.md` exists and is comprehensive
- [ ] `docs/QUICK_REFERENCE_AWS_EC2.md` exists
- [ ] Deployment script `scripts/deploy-to-aws-ec2.sh` is executable
- [ ] README.md includes deployment section

## ✅ Local Testing

```bash
# Test unified setup locally
docker-compose -f docker-compose.dev.yml up -d

# Verify all containers are running
docker-compose -f docker-compose.dev.yml ps

# Test Identity Service
curl http://localhost:8000/api/health/

# Test Product Service
curl http://localhost:8002/api/products/

# Check logs for errors
docker-compose -f docker-compose.dev.yml logs

# Cleanup
docker-compose -f docker-compose.dev.yml down
```

- [ ] All services start without errors
- [ ] Both databases are created
- [ ] Redis is accessible
- [ ] Network connectivity verified between services
- [ ] Migrations run successfully

## ✅ Pre-Deployment Verification

- [ ] All team members are informed of deployment
- [ ] Database backup procedure is documented
- [ ] Rollback procedure is documented
- [ ] Monitoring and logging are configured (optional)
- [ ] Team has EC2 access and SSH credentials
- [ ] Deployment windows scheduled (if applicable)

## ✅ Security Review

- [ ] All passwords are unique and strong
- [ ] Secrets are not committed to Git
- [ ] `.env` file is in `.gitignore`
- [ ] AWS credentials are not hardcoded
- [ ] SSL/TLS certificates are prepared
- [ ] Security groups restrict access appropriately
- [ ] Database is not exposed to public internet
- [ ] Redis is not exposed to public internet

## ✅ Production Configuration

- [ ] `DEBUG` is set to `False`
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `SECRET_KEY` is unique and secure
- [ ] Database backups are automated
- [ ] Log monitoring is configured
- [ ] Error tracking is configured (optional)
- [ ] Email notifications are configured (optional)

## ✅ DNS & Domain Setup

- [ ] Domain is registered (if using custom domain)
- [ ] DNS records are configured:
  - [ ] A record points to EC2 Elastic IP
  - [ ] Optional: CNAME records for subdomains
- [ ] DNS propagation verified (24-48 hours typical)

## ✅ Nginx & SSL (Optional but Recommended)

- [ ] Nginx configuration template is prepared
- [ ] SSL certificate generation method documented
- [ ] Let's Encrypt configuration documented
- [ ] Domain verification prepared

## ✅ Backup & Recovery

- [ ] Backup script is created and tested
- [ ] Backup location is determined
- [ ] Backup retention policy is documented
- [ ] Restore procedure is tested
- [ ] Automated backup scheduler configured

## ✅ Monitoring & Alerts (Optional)

- [ ] CloudWatch monitoring configured (if using AWS)
- [ ] Email alerts configured
- [ ] Log aggregation configured (optional)
- [ ] Performance monitoring configured
- [ ] Disk space alerts configured

## ✅ Final Checks Before Deployment

1. **Code Quality**
   ```bash
   # Run linting
   flake8 identity-service/
   flake8 product-service/
   
   # Run tests
   docker-compose -f docker-compose.dev.yml exec identity-service pytest
   docker-compose -f docker-compose.dev.yml exec product-service pytest
   ```

2. **Image Verification**
   ```bash
   # Build images
   docker-compose -f docker-compose.prod.yml build
   
   # Test images locally
   docker-compose -f docker-compose.prod.yml up -d
   docker-compose -f docker-compose.prod.yml ps
   docker-compose -f docker-compose.prod.yml down
   ```

3. **Documentation Review**
   - [ ] All guides are up-to-date
   - [ ] Commands are tested and verified
   - [ ] Troubleshooting section is comprehensive
   - [ ] Contact information is current

## 🚀 Deployment Readiness

- [ ] All checklist items completed
- [ ] Team is briefed and ready
- [ ] Backup verified and tested
- [ ] Rollback procedure ready
- [ ] Monitoring is active
- [ ] Communication channels open

---

## Deployment Day Checklist

1. **Pre-Deployment (T-15 minutes)**
   - [ ] Verify EC2 instance is running
   - [ ] Test SSH access to EC2
   - [ ] Verify security groups are configured
   - [ ] Confirm backups are current

2. **Deployment (T-0 minutes)**
   - [ ] Run deployment script or manual steps
   - [ ] Monitor service startup
   - [ ] Verify all containers are running
   - [ ] Check logs for errors

3. **Post-Deployment (T+15 minutes)**
   - [ ] Test all API endpoints
   - [ ] Verify database connectivity
   - [ ] Check Redis connectivity
   - [ ] Monitor resource usage
   - [ ] Review logs for warnings

4. **Validation (T+1 hour)**
   - [ ] Smoke tests passed
   - [ ] No critical errors in logs
   - [ ] Performance metrics acceptable
   - [ ] Backups working
   - [ ] Monitoring active

---

## Contact & Support

- **Infrastructure Team**: [contact info]
- **Development Team**: [contact info]
- **On-Call Engineer**: [contact info]
- **Escalation Path**: [procedure]

---

## Sign-Off

- [ ] Infrastructure Lead: _________________ Date: _______
- [ ] Development Lead: _________________ Date: _______
- [ ] DevOps Engineer: _________________ Date: _______
- [ ] Project Manager: _________________ Date: _______

---

**Last Updated**: [Current Date]  
**Next Review**: [30 days from now]

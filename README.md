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

# 🔥 Optional (Add Badge at top)

Add this at the top:

```markdown
![CI](https://github.com/Logical-Coder/commerce-platform/actions/workflows/ci-cd.yml/badge.svg)
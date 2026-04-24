# CI/CD Pipeline Explanation

This project uses GitHub Actions to automatically check code quality, run tests, build Docker image, and deploy the application.

## Pipeline Flow

```text
Developer pushes code
        ↓
GitHub Actions starts
        ↓
Run tests + coverage
        ↓
Run linting and formatting checks
        ↓
Build Docker image
        ↓
Push image to GitHub Container Registry
        ↓
Deploy to server using SSH
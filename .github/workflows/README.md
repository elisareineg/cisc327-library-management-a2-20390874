# GitHub Actions Workflows

This directory contains GitHub Actions workflows for CI/CD automation of the Library Management System.

## Workflows

### 1. `ci.yml` - Main CI/CD Pipeline

- **Triggers**: Push to main/develop branches, pull requests to main
- **Jobs**:
  - **Test**: Runs tests across Python 3.8-3.12 with coverage reporting
  - **Lint**: Code formatting and linting checks (black, isort, flake8)
  - **Build**: Creates deployment artifacts
  - **Security**: Security scanning with bandit and safety

### 2. `deploy.yml` - Production Deployment

- **Triggers**: Push to main branch or version tags
- **Jobs**:
  - **Deploy**: Deploys to production environment
  - **Health Check**: Verifies deployment success

### 3. `feature-branch.yml` - Feature Branch Testing

- **Triggers**: Push to feature/_, bugfix/_, hotfix/\* branches
- **Jobs**:
  - **Test Feature**: Runs tests with coverage requirements
  - **Function-specific tests**: Runs tests based on branch name

### 4. `nightly.yml` - Nightly Build and Test

- **Triggers**: Daily at 2 AM UTC, manual trigger
- **Jobs**:
  - **Nightly Test**: Comprehensive testing with parallel execution
  - **Performance Tests**: Performance benchmarking
  - **Report Generation**: Detailed test reports

## Setup Instructions

1. **Enable GitHub Actions**: Go to your repository Settings > Actions > General
2. **Configure Secrets**: Add any required secrets in Settings > Secrets and variables > Actions
3. **Set up Environments**: Create production environment in Settings > Environments
4. **Configure Branch Protection**: Set up branch protection rules for main branch

## Required Secrets

- `PRODUCTION_HOST`: Production server hostname/IP
- `PRODUCTION_USER`: Production server username
- `PRODUCTION_KEY`: SSH private key for production server

## Dependencies

The workflows expect the following files in your repository:

- `requirements.txt`: Python dependencies
- `tests/`: Test directory with pytest tests
- `library_service.py`: Main application code

## Customization

You can customize the workflows by:

- Modifying Python versions in the matrix strategy
- Adding additional test commands
- Configuring deployment targets
- Adjusting security scanning rules
- Setting custom coverage thresholds

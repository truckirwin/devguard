# Development Environment Setup Guide

## The Writers Room – AWS-Native Creative Writing IDE

---

## 1. Prerequisites

- **Operating System**: macOS, Linux, or Windows (WSL2 recommended)
- **Node.js**: v18+
- **Python**: 3.10+
- **Docker**: Latest stable
- **AWS CLI**: v2+
- **Git**: Latest stable
- **VS Code**: Forked version (see repo instructions)
- **Terraform** (if using for IaC): v1.5+

---

## 2. Clone the Repository

```sh
git clone <repo-url>
cd TheWritersRoom
```

---

## 3. Install Dependencies

### Node.js (UI, API Gateway mocks)
```sh
npm install
```

### Python (backend, Lambdas)
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Environment Variables

- Copy `.env.example` to `.env` and fill in required values:
  - AWS credentials/profile
  - Database connection strings (Aurora, DynamoDB, etc.)
  - S3 bucket names
  - Cognito pool IDs
  - API endpoints

---

## 5. AWS Credentials & Configuration

- Configure AWS CLI:
```sh
aws configure
```
- Use named profiles for dev/staging/prod as needed.
- Ensure your IAM user/role has least-privilege access for development resources.

---

## 6. Running Services Locally

### UI (VS Code fork)
```sh
cd ui
npm run dev
```

### Backend (API mocks, Lambdas)
```sh
cd src
npm run start:local  # or use `sam local`/`serverless offline` for AWS Lambda emulation
```

### Database (optional: local Aurora/Postgres, DynamoDB Local)
- Use Docker Compose or AWS-provided local images for local DB emulation.

---

## 7. Docker (Optional, for full-stack local dev)

```sh
docker compose up
```

---

## 8. Troubleshooting

- **Common Issues**:
  - Missing environment variables: Check `.env` file
  - AWS permissions: Verify IAM role and AWS CLI config
  - Port conflicts: Change default ports in config files
  - Dependency errors: Run `npm install` or `pip install -r requirements.txt` again
- **Logs**:
  - UI: `ui/logs/`
  - Backend: `logs/` or console output
- **Contact**: Reach out to the team via Slack or email for help

---

## 9. Additional Resources

- [AWS Developer Tools](https://aws.amazon.com/developer/tools/)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Terraform Docs](https://www.terraform.io/docs)

---

## Conclusion

You are now ready to develop, test, and contribute to The Writers Room. For advanced setup or CI/CD, see the IaC and DevOps documentation. 
# Deploy Final — FastAPI on AWS

## Project Overview

REST API built with FastAPI: CRUD items in PostgreSQL (RDS), upload and download files via Amazon S3. The app runs in Docker on EC2; GitHub Actions deploys on push to `main`.

## Architecture

```text
Developer → GitHub → GitHub Actions (SSH)
                         ↓
Internet → EC2 (Docker: FastAPI) → RDS PostgreSQL (private)
                         ↓
                    Amazon S3
IAM: EC2 instance role for S3; IAM user optional for CLI
```

## Prerequisites

- AWS account, GitHub account
- Tools: Git, Docker, AWS CLI
- EC2 key pair (`.pem`)

## Local Development

```bash
cp .env.example .env
docker compose up -d --build
```

Open http://localhost:8001/docs (host port 8001; EC2 uses 8000)

Local Postgres is provided by `docker-compose.yml`. For S3 uploads locally, set `S3_BUCKET_NAME` and AWS credentials (`aws configure` or env vars).

## AWS Resources

| Resource | Purpose |
|----------|---------|
| IAM user | CLI / optional CI |
| IAM role `ec2-s3-app-role` | S3 access from EC2 |
| RDS PostgreSQL 14 `mssv-db` | Application database |
| S3 `mssv-bucket-*` | File storage |
| EC2 + security groups | Run Docker container |
| GitHub Secrets | CI/CD deploy |

### Part 1 — IAM

1. Create IAM user, attach `iam/github-actions-policy.json` (adjust as needed).
2. Create role for EC2, attach `iam/ec2-s3-policy.json` (replace `YOUR_BUCKET_NAME`).
3. Attach role to EC2 instance (Instance profile).

### Part 2 — RDS

- Engine PostgreSQL 14, `db.t3.micro`, 20 GiB gp2
- Identifier: `mssv-db`
- Default VPC, **Public access: No**
- Security group: inbound **5432** from EC2 security group only
- `DATABASE_URL`: `postgresql://postgres:<password>@<endpoint>:5432/postgres`

### Part 3 — S3

- Bucket name `mssv-bucket-<random>`, region `us-east-1`
- Block public access enabled, versioning disabled
- EC2 role policy allows Put/Get/Delete on that bucket

### Part 5 — EC2

1. Run `scripts/ec2-bootstrap.sh` on the instance (log out and back in after Docker group change).
2. Clone repo to `~/deploy-final`.
3. Create `~/deploy-final/.env` from `.env.example` (RDS URL + bucket name).
4. Deploy:

```bash
cd ~/deploy-final
docker compose -f docker-compose.prod.yml up -d --build
```

Security group: **22** from your IP, **8000** from `0.0.0.0/0` (lab).

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `AWS_REGION` | e.g. `us-east-1` |
| `S3_BUCKET_NAME` | Target S3 bucket |
| `APP_NAME` | API title in Swagger |

On EC2, prefer IAM role for S3 (no access keys in `.env`).

## Deployment (CI/CD)

GitHub → Settings → Secrets and variables → Actions:

| Secret | Value |
|--------|--------|
| `EC2_HOST` | Public IP or DNS |
| `EC2_USER` | `ec2-user` (Amazon Linux) or `ubuntu` |
| `EC2_SSH_KEY` | Full `.pem` contents |
| `DATABASE_URL` | RDS URL (optional if `.env` already on server) |
| `AWS_REGION` | `us-east-1` |
| `S3_BUCKET_NAME` | Your bucket |
| `AWS_ACCESS_KEY_ID` | Optional, not required for SSH-only deploy |
| `AWS_SECRET_ACCESS_KEY` | Optional |

Push to `main` triggers `.github/workflows/deploy.yml`.

## API Documentation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health + DB + S3 config |
| GET/POST | `/items` | List / create items |
| GET/PATCH/DELETE | `/items/{id}` | Item CRUD |
| POST | `/files/upload` | Upload multipart file to S3 |
| GET | `/files` | List uploaded files |
| GET | `/files/{id}/download` | Download file |
| DELETE | `/files/{id}` | Delete S3 object + record |

Interactive docs: `/docs`

## Screenshots Checklist

- IAM user and EC2 role policies
- RDS instance and security group
- S3 bucket settings, Postman upload, object in bucket
- `docker ps` and browser `/docs` (local and EC2)
- EC2 instance, public URL
- GitHub secrets, successful workflow run

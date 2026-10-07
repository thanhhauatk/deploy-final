# AWS setup order

## 1. S3

Create bucket `mssv-bucket-<random>` in `us-east-1`, block public access, versioning off.

## 2. IAM role for EC2

1. IAM → Roles → Create → AWS service → EC2.
2. Create policy from `iam/ec2-s3-policy.json` (replace bucket name).
3. Attach policy to role, name e.g. `ec2-s3-app-role`.

## 3. IAM user (Part 1 screenshot)

1. Create user `dev-<mssv>`.
2. Attach `iam/github-actions-policy.json` or custom minimal policy.
3. Create access key for AWS CLI on your laptop (do not commit).

## 4. RDS

1. Create PostgreSQL 14, `db.t3.micro`, 20 GiB, identifier `mssv-db`.
2. Master: `postgres`, password of your choice.
3. Default VPC, public access **No**.
4. Create security group `rds-sg`: inbound 5432 from EC2 security group (add rule after EC2 exists).

## 5. EC2

1. Amazon Linux 2023, `t3.micro`, public IP.
2. Security group `ec2-sg`: SSH 22 (your IP), TCP 8000 (0.0.0.0/0 for lab).
3. Attach instance profile `ec2-s3-app-role`.
4. SSH in, run:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/scripts/ec2-bootstrap.sh | bash
```

Or copy `scripts/ec2-bootstrap.sh` and run it.

5. Log out and SSH again, then:

```bash
git clone https://github.com/YOUR_USER/YOUR_REPO.git ~/deploy-final
cp ~/deploy-final/.env.example ~/deploy-final/.env
nano ~/deploy-final/.env
cd ~/deploy-final
docker compose -f docker-compose.prod.yml up -d --build
```

6. Open `http://<public-ip>:8000/docs`.

## 6. GitHub

Push this project to GitHub. Add secrets listed in README. Push to `main` to deploy.

## 7. Screenshots

Capture each console page and Postman/browser tests listed in README.

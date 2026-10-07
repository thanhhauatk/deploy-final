# Báo Cáo Triển Khai FastAPI Trên AWS

## 1. Tổng quan dự án
Ứng dụng REST API viết bằng FastAPI, container hóa bằng Docker và triển khai tự động lên AWS EC2 qua GitHub Actions.
- **Backend:** FastAPI (Python 3.11), SQLAlchemy.
- **Database:** PostgreSQL 14 trên Amazon RDS (Private Subnet).
- **Lưu trữ:** Amazon S3 lưu file upload/download.
- **Máy chủ:** Amazon EC2 (Amazon Linux 2023) chạy Docker.
- **CI/CD:** GitHub Actions tự động build và deploy khi push code lên nhánh `main`.

---

## 2. Sơ đồ kiến trúc

```text
[Người dùng] ---> HTTP 8000 ---> [EC2: FastAPI (Docker)] ---> RDS PostgreSQL 14 (Private)
                                           |
                                      IAM Role S3
                                           v
[GitHub Actions] ---> SSH 22 ---> [Amazon S3 Bucket]
```

---

## 3. Yêu cầu môi trường
- Tài khoản AWS (Region `us-east-1`).
- Công cụ: Python 3.11+, Docker Desktop, Git, SSH Client.
- File SSH Key: `HauVT17-key.pem`.

---

## 4. Chạy thử nghiệm Local
```bash
# 1. Tạo file cấu hình
cp .env.example .env

# 2. Khởi chạy app và database local
docker compose up -d --build
```
- Swagger UI local: `http://localhost:8001/docs`
- Kiểm tra trạng thái: `http://localhost:8001/health`

---

## 5. Danh sách tài nguyên AWS đã tạo

| Dịch vụ | Tên tài nguyên | Thông số | Mục đích |
| :--- | :--- | :--- | :--- |
| **IAM User** | `fastapi_deployer` | Quyền CLI & CI | Quản trị triển khai |
| **IAM Role** | `ec2-s3-app-role` | Quyền đọc/ghi S3 | Gắn vào EC2 truy cập S3 |
| **RDS** | `hauvt17-db` | PostgreSQL 14, `db.t3.micro` | Database chính của app |
| **S3** | `fastapi-app-files-nmp2026`| Region `us-east-1` | Lưu trữ file upload |
| **EC2** | `HauVT17-Web-Server` | `t3.micro`, IP: `44.195.67.82` | Máy chủ chạy ứng dụng |

---

## 6. Biến môi trường (.env)

| Biến | Giá trị | Ý nghĩa |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://postgres:Thanhhau@hauvt17-db.cy9ykkoeugi5.us-east-1.rds.amazonaws.com:5432/postgres` | Kết nối RDS |
| `AWS_REGION` | `us-east-1` | Vùng AWS |
| `S3_BUCKET_NAME`| `fastapi-app-files-nmp2026` | Bucket S3 |
| `APP_NAME` | `fastapi-app` | Tên API |

---

## 7. Các bước triển khai (Deploy)

### Deploy thủ công trên EC2:
```bash
ssh -i "HauVT17-key.pem" ec2-user@44.195.67.82
git clone https://github.com/thanhhauatk/deploy-final.git ~/deploy-final
cd ~/deploy-final
docker compose -f docker-compose.prod.yml up -d --build
```

### Deploy tự động bằng GitHub Actions:
Cấu hình GitHub Secrets (`Settings -> Secrets and variables -> Actions`):
- `EC2_HOST`: `44.195.67.82`
- `EC2_USER`: `ec2-user`
- `EC2_SSH_KEY`: Nội dung file `HauVT17-key.pem`
- `DATABASE_URL`, `AWS_REGION`, `S3_BUCKET_NAME`

Mỗi khi push commit lên nhánh `main`, pipeline `.github/workflows/deploy.yml` sẽ tự động deploy.

---

## 8. Danh sách API (Swagger UI)
Truy cập trực tiếp: `http://44.195.67.82:8000/docs`

- `GET /health`: Kiểm tra API và kết nối Database/S3.
- `GET, POST /items`: Xem và thêm mới dữ liệu vào RDS.
- `GET, PATCH, DELETE /items/{id}`: Xem chi tiết, sửa và xoá dữ liệu.
- `POST /files/upload`: Upload file trực tiếp lên S3.
- `GET /files`: Xem danh sách file đã tải lên.
- `GET /files/{id}/download`: Tải file từ S3 về máy.
- `DELETE /files/{id}`: Xoá file trên S3.

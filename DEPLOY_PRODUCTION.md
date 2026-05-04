# Production Deploy

## Mục tiêu

File này dùng cho deploy production bằng Docker Compose trên một VPS Linux.

Khác với `docker-compose.yml` dùng cho local dev:

- không mount source code vào container
- không mở port `postgres` và `redis` ra ngoài host
- backend không chạy `--reload`
- frontend chạy `build + start`

## 1. Chuẩn bị server

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable --now docker
```

## 2. Pull code

```bash
git clone <repo-url> ~/crm
cd ~/crm
```

## 3. Tạo file `.env`

```bash
cp .env.example .env
nano .env
```

Các giá trị production tối thiểu nên sửa:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/crm
REDIS_URL=redis://redis:6379/0

JWT_SECRET=<random-secret>
DEFAULT_ADMIN_EMAIL=<admin-email>
DEFAULT_ADMIN_PASSWORD=<strong-password>

NEXT_PUBLIC_API_BASE_URL=/api
BACKEND_PUBLIC_BASE_URL=https://crm.example.com
FRONTEND_PUBLIC_BASE_URL=https://crm.example.com
CORS_ORIGINS=
PUBLIC_DOMAIN=crm.example.com
ACME_EMAIL=ops@example.com

SEED_DEMO_DATA=false
```

Nếu dùng tích hợp thật thì điền thêm:

- `FB_SYSTEM_USER_TOKEN`
- `FB_BUSINESS_ID`
- `LARK_WEBHOOK_URL`
- `SEPAY_WEBHOOK_SECRET`
- `SEPAY_API_TOKEN`
- `SEPAY_BANK_ACCOUNT_ID`
- `TRONGRID_API_KEY`
- `AGENCY_USDT_WALLET`
- `USDT_TRC20_CONTRACT`
- `SMIT_BASE_URL`
- `SMIT_API_KEY`
- `SMIT_SYNC_URL_TEMPLATE`

## 4. Chạy production stack

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## 5. Kiểm tra

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```

Health checks:

- Public HTTP: `http://<domain>/`
- Public HTTPS: `https://<domain>/`
- Backend health via proxy: `https://<domain>/health`
- API readiness via proxy: `https://<domain>/api/ops/ready`

## 6. Reverse proxy

Repo đã có sẵn reverse proxy Caddy trong:

- [deploy/caddy/Caddyfile](/Users/khanhnh/crm/deploy/caddy/Caddyfile)

Luồng hiện tại:

- `/` -> frontend
- `/api/` -> backend
- `/health` -> backend health

Điều kiện để HTTPS tự lên:

- `PUBLIC_DOMAIN` phải trỏ đúng về public IP server
- inbound `80` và `443` phải mở trong Security Group
- `ACME_EMAIL` nên là email thật để nhận cảnh báo chứng chỉ

Sau khi deploy production compose, truy cập:

- `https://<domain>/login`
- `https://<domain>/api/ops/ready`

## 7. Các lưu ý quan trọng

- Không expose `postgres` và `redis` ra ngoài internet.
- Không dùng `docker-compose.yml` local để deploy production.
- Nếu host đã có PostgreSQL native chạy ở `5432`, điều đó không ảnh hưởng vì file production này không bind port DB ra host.
- Security Group cần mở `80` và `443` để Caddy lấy chứng chỉ và phục vụ HTTPS.
- Không cần mở `3000` hoặc `8000` nếu dùng file production này.
- Mỗi lần update code:

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## 8. Backup tối thiểu

Dump database:

```bash
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U postgres crm > backup.sql
```

Backup thêm:

- file `.env`
- thư mục volume Docker nếu cần retention đầy đủ

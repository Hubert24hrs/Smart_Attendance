# Smart Attendance Platform - Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- Domain name (for SSL)
- VPS with at least 2GB RAM

---

## Quick Start (Development)

```bash
# 1. Start Backend
cd smart_attendance
python -m uvicorn app.main:app --reload --port 8000

# 2. Start Frontend (separate terminal)
cd frontend
npm run dev
```

---

## Production Deployment (Self-Hosted)

### Step 1: Prepare Environment

Create `.env` file in project root:

```env
# Database
POSTGRES_USER=attendance
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=attendance_db

# Security
SECRET_KEY=generate_a_64_char_random_string_here

# Optional: Email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Step 2: Build & Run

```bash
# Production with all services
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 3: Access

| URL | Service |
|-----|---------|
| http://localhost | React Dashboard |
| http://localhost/api/v1 | Backend API |
| http://localhost/docs | API Documentation |

---

## SSL with Let's Encrypt

### Option A: Nginx Proxy Manager (Easiest)

1. Deploy Nginx Proxy Manager container
2. Add proxy host for your domain
3. Enable SSL with Let's Encrypt

### Option B: Certbot

```bash
# Install certbot
apt install certbot

# Get certificate
certbot certonly --standalone -d yourdomain.com

# Update nginx/nginx.conf with SSL paths
```

---

## Scaling

### Horizontal Scaling
```bash
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Database Backup
```bash
docker exec attendance_db pg_dump -U attendance attendance_db > backup.sql
```

---

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
docker-compose logs -f api
docker-compose logs -f postgres
```

---

## Mobile App Deployment

### Android (Play Store)
```bash
cd mobile_app
flutter build appbundle --release
# Upload to Google Play Console
```

### iOS (App Store)
```bash
flutter build ios --release
# Open in Xcode and archive
```

---

## API Endpoints Summary

| Endpoint | Description |
|----------|-------------|
| `/api/v1/auth/token` | Login |
| `/api/v1/institutions` | Manage institutions |
| `/api/v1/students` | Student management |
| `/api/v1/sessions` | Attendance sessions |
| `/api/v1/analytics` | Reports & trends |
| `/api/v1/billing` | Subscription management |
| `/api/v1/notifications` | Push notifications |

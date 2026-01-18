# Smart Attendance Platform

> **Multi-tenant SaaS for Face Recognition Attendance** - Built for schools, colleges, and institutions worldwide.

[![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](https://github.com/Hubert24hrs/Smart_Attendance)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18+-blue.svg)](https://react.dev)
[![Flutter](https://img.shields.io/badge/flutter-3.0+-blue.svg)](https://flutter.dev)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Face Recognition** | AI-powered attendance with N-frame consistency |
| 🏛️ **Multi-Tenancy** | Each institution gets isolated data |
| 👥 **Role-Based Access** | SuperAdmin → Admin → Teacher |
| 📊 **Analytics** | Attendance trends, course stats, alerts |
| 💳 **Subscription Billing** | Free, Basic, Pro, Enterprise tiers |
| 🔔 **Notifications** | Email and push notification support |
| 📱 **Mobile App** | Flutter app for teachers |
| 🐳 **Docker Ready** | One-command deployment |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or SQLite for dev)

### Installation

```bash
# Clone
git clone https://github.com/Hubert24hrs/Smart_Attendance.git
cd Smart_Attendance

# Backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Access
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
smart_attendance/
├── app/                    # FastAPI Backend
│   ├── api/               # API endpoints
│   │   ├── auth.py        # Authentication
│   │   ├── institutions.py # Multi-tenant management
│   │   ├── analytics.py   # Reports & trends
│   │   ├── billing.py     # Subscription management
│   │   └── notifications.py # Push notifications
│   ├── db/models.py       # SQLAlchemy models
│   └── services/          # Business logic
├── frontend/              # React + Tailwind SPA
├── mobile_app/           # Flutter teacher app
├── docker-compose.yml     # Development
└── docker-compose.prod.yml # Production
```

---

## 🔧 API Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `POST /api/v1/auth/token` | Public | Login |
| `GET /api/v1/institutions` | SuperAdmin | List institutions |
| `POST /api/v1/billing/subscribe` | Admin | Subscribe to plan |
| `GET /api/v1/analytics/overview` | Admin+ | Attendance stats |
| `POST /api/v1/notifications/send` | Admin+ | Send notification |

---

## 🐳 Docker Deployment

```bash
# Production
docker-compose -f docker-compose.prod.yml up -d --build

# Development
docker-compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full guide.

---

## 📱 Mobile App

```bash
cd mobile_app
flutter run
```

Configure backend URL in `lib/services/api_service.dart`.

---

## 💳 Subscription Tiers

| Tier | Students | Price/mo |
|------|----------|----------|
| Free | 50 | $0 |
| Basic | 500 | $29.99 |
| Pro | 2000 | $79.99 |
| Enterprise | Unlimited | $199.99 |

---

## 🔒 Security

- JWT authentication with bcrypt password hashing
- Tenant isolation middleware
- Rate limiting (slowapi)
- CORS configuration
- Role-based access control

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

Built by [Hubert24hrs](https://github.com/Hubert24hrs)

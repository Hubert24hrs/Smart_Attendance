# Smart Classroom Attendance System

A production-grade face recognition attendance system for educational institutions. Teachers capture classroom footage, and the backend automatically identifies students using facial recognition.

## 🔹 Features

- **Face Recognition** - Uses `face_recognition` (dlib-based) for accurate student identification
- **JWT Authentication** - Secure teacher/admin login
- **Web Dashboard** - Enroll students, manage sessions, view reports
- **Capture Client** - Python/OpenCV script for teacher's camera
- **Anti-Cheating** - Students cannot self-mark attendance

## 🔹 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI**: face_recognition, OpenCV, NumPy
- **Auth**: JWT (python-jose), bcrypt
- **Frontend**: Jinja2 Templates

## 🔹 Installation

```bash
# Clone the repository
git clone https://github.com/Hubert24hrs/Smart_Attendance.git
cd Smart_Attendance

# Install dependencies
pip install -r requirements.txt

# Install dlib (pre-compiled binary)
pip install dlib-bin
pip install face_recognition --no-deps
pip install click Pillow face_recognition_models
```

## 🔹 Running the System

### Start the Server
```bash
python -m uvicorn app.main:app --reload
```

### Access Points
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs

### Register a Teacher
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher1","password":"secure123"}'
```

### Run the Capture Client
```bash
cd client
python teacher_capture.py
```

## 🔹 Project Structure

```
smart_attendance/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── core/                # Config, Security
│   ├── db/                  # Database, Models
│   ├── api/                 # REST endpoints
│   ├── routers/             # Dashboard views
│   ├── services/            # Face recognition logic
│   └── templates/           # HTML templates
├── client/
│   └── teacher_capture.py   # Camera capture script
└── requirements.txt
```

## 🔹 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register teacher |
| `/auth/token` | POST | Login (get JWT) |
| `/students/enroll` | POST | Enroll student with photos |
| `/students/` | GET | List all students |
| `/sessions/start` | POST | Start attendance session |
| `/sessions/{id}/process_frame` | POST | Send camera frame |
| `/sessions/{id}/end` | POST | End session |
| `/sessions/{id}/report` | GET | Get attendance report |

## 🔹 Security Design

1. **Teacher-Controlled Only** - Students cannot self-mark attendance
2. **JWT Tokens** - All API calls require authentication  
3. **Session Windows** - Attendance only during active sessions
4. **Face Embeddings** - Only 128-d vectors stored, not raw images

## 🔹 License

MIT License

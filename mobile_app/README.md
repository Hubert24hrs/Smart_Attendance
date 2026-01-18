# Smart Attendance - Mobile Capture App

Flutter mobile application for teachers to capture attendance using phone camera.

## Features

- 📱 Login with teacher credentials
- 📷 Live camera preview
- 🎯 Auto-capture frames every 2 seconds
- 👤 Real-time student recognition display
- ✅ Session start/end controls

## Setup

1. **Configure Backend URL**
   
   Edit `lib/services/api_service.dart`:
   ```dart
   // For Android Emulator:
   static String baseUrl = 'http://10.0.2.2:8000';
   
   // For physical device (use your computer's IP):
   static String baseUrl = 'http://192.168.x.x:8000';
   ```

2. **Run the App**
   ```bash
   cd mobile_app
   flutter run
   ```

## Screens

- **Login Screen**: Teacher enters username/password
- **Capture Screen**: Camera preview with session controls

## Backend Requirements

Ensure the FastAPI backend is running:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Note: Use `--host 0.0.0.0` to make it accessible from mobile devices on the same network.

import cv2
import requests
import getpass

# CONFIG
API_URL = "http://localhost:8000"
SESSION_ID = None
TOKEN = None


def login():
    global TOKEN
    print("=== Teacher Login ===")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    try:
        resp = requests.post(
            f"{API_URL}/auth/token", data={"username": username, "password": password}
        )
        if resp.status_code == 200:
            TOKEN = resp.json()["access_token"]
            print("Login Successful!")
            return True
        else:
            print("Login Failed:", resp.text)
            return False
    except Exception as e:
        print(f"Connection Error: {e}")
        return False


def start_session():
    global SESSION_ID
    course = input("Enter Course Name: ")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    resp = requests.post(
        f"{API_URL}/sessions/start?course_name={course}", headers=headers
    )
    if resp.status_code == 200:
        SESSION_ID = resp.json()["session_id"]
        print(f"Session {SESSION_ID} Started!")
        return True
    else:
        print("Failed to start session:", resp.text)
        return False


def capture_loop():
    cap = cv2.VideoCapture(0)  # 0 for default Webcam

    print("Starting Capture... Press 'q' to stop.")
    frame_count = 0

    headers = {"Authorization": f"Bearer {TOKEN}"}

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        cv2.imshow("Teacher Capture Client", frame)

        # Send frame every ~1 second (30 frames) to avoid overloading server
        if frame_count % 30 == 0:
            _, img_encoded = cv2.imencode(".jpg", frame)
            files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}

            try:
                # Async send in real app, sync here for simplicity
                res = requests.post(
                    f"{API_URL}/sessions/{SESSION_ID}/process_frame",
                    files=files,
                    headers=headers,
                )
                print(f"Frame {frame_count}: {res.json()}")
            except Exception as e:
                print(f"Error sending frame: {e}")

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    # End Session
    requests.post(f"{API_URL}/sessions/{SESSION_ID}/end", headers=headers)
    print("Session Ended.")


def main():
    if not login():
        return

    # Option: Enroll or Start Session
    mode = input("Select Mode: [1] Start Attendance Session  [2] Enroll Student : ")

    if mode == "1":
        if start_session():
            capture_loop()
    elif mode == "2":
        print(
            "For Enrollment, please use the Web Admin Dashboard or API directly "
            "(Multipart upload required)."
        )
        # Could implement CLI enrollment here but it's complex with finding image files.
    else:
        print("Invalid option")


if __name__ == "__main__":
    main()

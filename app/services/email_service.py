import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.core.config import settings

class EmailService:
    """Email service for sending attendance reports"""
    
    @staticmethod
    def send_attendance_report(
        to_email: str,
        subject: str,
        course_name: str,
        date: str,
        attendance_data: List[dict]
    ) -> bool:
        """Send attendance report email to teacher"""
        
        if not settings.SMTP_HOST:
            print("SMTP not configured, skipping email")
            return False
        
        try:
            # Create HTML content
            html = f"""
            <html>
            <head>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; }}
                    .present {{ color: green; }}
                    .absent {{ color: red; }}
                </style>
            </head>
            <body>
                <h2>Attendance Report - {course_name}</h2>
                <p><strong>Date:</strong> {date}</p>
                <p><strong>Total Present:</strong> {len([a for a in attendance_data if a['status'] == 'PRESENT'])}</p>
                
                <table>
                    <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Time</th>
                    </tr>
            """
            
            for record in attendance_data:
                status_class = "present" if record['status'] == 'PRESENT' else "absent"
                html += f"""
                    <tr>
                        <td>{record.get('student_id', 'N/A')}</td>
                        <td>{record.get('name', 'Unknown')}</td>
                        <td class="{status_class}">{record['status']}</td>
                        <td>{record.get('time', 'N/A')}</td>
                    </tr>
                """
            
            html += """
                </table>
                <p>This is an automated email from Smart Attendance System.</p>
            </body>
            </html>
            """
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = to_email
            
            msg.attach(MIMEText(html, "html"))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

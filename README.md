Alerting & Notification Platform 🚀
This project is built as part of the SDE Intern Assignment for Atomic Ads.
It demonstrates the design and implementation of an alerting & notification system with support for admin features, user preferences, reminders, and analytics.
📌 Features
Admin APIs
Create, list, and archive alerts
Configure severity, delivery type, visibility (org/team/user), start & expiry time
User APIs
View alerts assigned to them
Mark alerts as read/unread
Snooze alerts
Notification Service
Reminder triggers for active alerts
Analytics
Track total alerts
Delivered vs. Read
Snoozed alerts
Severity breakdown
Health Check & Root Routes
/ → Welcome message
/health → App status check
⚙️ Tech Stack
Python 3.13+
FastAPI (for APIs)
Uvicorn (ASGI server)
Pydantic (data validation)
Requests (for API testing)
📂 Project Structure
Alerting-Platform/
│── app.py              # Main FastAPI application
│── requirements.txt    # Python dependencies
│── README.md           # Documentation
│── test_alerting_api.py # Script to test API endpoints
🚀 Setup & Run
1. Clone the repo
git clone https://github.com/<your-username>/alerting-platform.git
cd alerting-platform
2. Install dependencies
pip install -r requirements.txt
3. Run the app
uvicorn app:app --reload
App will be live at:
👉 http://127.0.0.1:8000
🔗 API Endpoints
Root & Health
GET / → Welcome message
GET /health → App status
Admin
POST /admin/alerts → Create alert
GET /admin/alerts → List alerts
POST /admin/alerts/{id}/archive → Archive alert
User
GET /user/{user_id}/alerts → Get user alerts
POST /user/snooze → Snooze alert
POST /user/mark_read → Mark alert as read
POST /user/mark_unread → Mark alert as unread
Reminders
POST /trigger_reminders → Trigger reminder deliveries
Analytics
GET /analytics → View analytics report
📊 Sample Analytics Response
{
  "total_alerts_created": 1,
  "alerts_delivered_vs_read": {"delivered": 0, "read": 0},
  "snoozed_counts_per_alert": {},
  "breakdown_by_severity": {"Info": 1, "Warning": 0, "Critical": 0}
}
🙌 Author
Shivam Kumar
Email: shivamkr1739@gmail.com
LinkedIn: linkedin.com/in/shivam-kumar-5790a2214
✨ This project was created as part of the Atomic Ads SDE Intern hiring assignment.

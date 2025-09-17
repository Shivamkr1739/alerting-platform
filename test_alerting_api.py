import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def create_alert():
    url = f"{BASE_URL}/admin/alerts"
    payload = {
        "title": "Server Downtime",
        "message": "The server will be down for maintenance at midnight.",
        "severity": "Info",
        "delivery_type": "InApp",
        "start_time": "2024-06-01T00:00:00",
        "expiry_time": "2024-06-02T00:00:00",
        "visibility_org": False,
        "visibility_teams": [1],
        "visibility_users": []
    }
    response = requests.post(url, json=payload)
    print("Create Alert Response:", response.status_code)
    print(response.json())
    return response.json().get("id")

def list_alerts():
    url = f"{BASE_URL}/admin/alerts"
    response = requests.get(url)
    print("List Alerts Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def get_user_alerts(user_id):
    url = f"{BASE_URL}/user/{user_id}/alerts"
    response = requests.get(url)
    print(f"User  {user_id} Alerts Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def snooze_alert(user_id, alert_id):
    url = f"{BASE_URL}/user/snooze"
    payload = {"user_id": user_id, "alert_id": alert_id}
    response = requests.post(url, json=payload)
    print("Snooze Alert Response:", response.status_code)
    print(response.json())

def mark_read(user_id, alert_id):
    url = f"{BASE_URL}/user/mark_read"
    payload = {"user_id": user_id, "alert_id": alert_id}
    response = requests.post(url, json=payload)
    print("Mark Read Response:", response.status_code)
    print(response.json())

def mark_unread(user_id, alert_id):
    url = f"{BASE_URL}/user/mark_unread"
    payload = {"user_id": user_id, "alert_id": alert_id}
    response = requests.post(url, json=payload)
    print("Mark Unread Response:", response.status_code)
    print(response.json())

def trigger_reminders():
    url = f"{BASE_URL}/trigger_reminders"
    response = requests.post(url)
    print("Trigger Reminders Response:", response.status_code)
    print(response.json())

def get_analytics():
    url = f"{BASE_URL}/analytics"
    response = requests.get(url)
    print("Analytics Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    alert_id = create_alert()
    list_alerts()
    get_user_alerts(user_id=1)
    if alert_id:
        snooze_alert(user_id=1, alert_id=alert_id)
        mark_read(user_id=1, alert_id=alert_id)
        mark_unread(user_id=1, alert_id=alert_id)
    trigger_reminders()
    get_analytics()
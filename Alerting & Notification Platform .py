from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date
from enum import Enum
from typing import List, Dict, Set, Optional

# Enums
class Severity(Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"

class DeliveryType(Enum):
    IN_APP = "InApp"
    EMAIL = "Email"
    SMS = "SMS"

class AlertStatus(Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"

class UserAlertState(Enum):
    UNREAD = "Unread"
    READ = "Read"
    SNOOZED = "Snoozed"

# Models
class Team:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class User:
    def __init__(self, id: int, name: str, team: Team):
        self.id = id
        self.name = name
        self.team = team

class Alert:
    def __init__(self, 
                 id: int,
                 title: str,
                 message: str,
                 severity: Severity,
                 delivery_type: DeliveryType,
                 start_time: datetime,
                 expiry_time: datetime,
                 reminder_frequency_hours: int = 2,
                 visibility_org: bool = False,
                 visibility_teams: Optional[Set[int]] = None,
                 visibility_users: Optional[Set[int]] = None,
                 status: AlertStatus = AlertStatus.ACTIVE,
                 reminders_enabled: bool = True):
        self.id = id
        self.title = title
        self.message = message
        self.severity = severity
        self.delivery_type = delivery_type
        self.start_time = start_time
        self.expiry_time = expiry_time
        self.reminder_frequency_hours = reminder_frequency_hours
        self.visibility_org = visibility_org
        self.visibility_teams = visibility_teams or set()
        self.visibility_users = visibility_users or set()
        self.status = status
        self.reminders_enabled = reminders_enabled

    def is_active(self, current_time: datetime) -> bool:
        return self.status == AlertStatus.ACTIVE and self.start_time <= current_time <= self.expiry_time

class NotificationDelivery:
    def __init__(self, alert_id: int, user_id: int, delivery_time: datetime):
        self.alert_id = alert_id
        self.user_id = user_id
        self.delivery_time = delivery_time

class UserAlertPreference:
    def __init__(self, user_id: int, alert_id: int):
        self.user_id = user_id
        self.alert_id = alert_id
        self.state = UserAlertState.UNREAD
        self.snoozed_date: Optional[date] = None  # date when snoozed

    def snooze(self, snooze_date: date):
        self.state = UserAlertState.SNOOZED
        self.snoozed_date = snooze_date

    def mark_read(self):
        self.state = UserAlertState.READ

    def mark_unread(self):
        self.state = UserAlertState.UNREAD

    def is_snoozed_today(self, today: date) -> bool:
        return self.state == UserAlertState.SNOOZED and self.snoozed_date == today

# Notification Channel Strategy
class NotificationChannel(ABC):
    @abstractmethod
    def send(self, user: User, alert: Alert):
        pass

class InAppChannel(NotificationChannel):
    def send(self, user: User, alert: Alert):
        # For MVP, just print or log
        print(f"[In-App] Alert to User {user.name}: {alert.title} - {alert.message}")

# Alert Manager (CRUD + visibility)
class AlertManager:
    def __init__(self):
        self.alerts: Dict[int, Alert] = {}
        self.next_alert_id = 1

    def create_alert(self, title: str, message: str, severity: Severity,
                     delivery_type: DeliveryType, start_time: datetime,
                     expiry_time: datetime, visibility_org: bool,
                     visibility_teams: Optional[Set[int]],
                     visibility_users: Optional[Set[int]],
                     reminder_frequency_hours: int = 2) -> Alert:
        alert = Alert(
            id=self.next_alert_id,
            title=title,
            message=message,
            severity=severity,
            delivery_type=delivery_type,
            start_time=start_time,
            expiry_time=expiry_time,
            reminder_frequency_hours=reminder_frequency_hours,
            visibility_org=visibility_org,
            visibility_teams=visibility_teams,
            visibility_users=visibility_users
        )
        self.alerts[self.next_alert_id] = alert
        self.next_alert_id += 1
        return alert

    def update_alert(self, alert_id: int, **kwargs):
        alert = self.alerts.get(alert_id)
        if not alert:
            raise ValueError("Alert not found")
        for key, value in kwargs.items():
            if hasattr(alert, key):
                setattr(alert, key, value)

    def archive_alert(self, alert_id: int):
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ARCHIVED

    def list_alerts(self, severity: Optional[Severity] = None,
                    status: Optional[AlertStatus] = None,
                    audience_user_id: Optional[int] = None,
                    audience_team_id: Optional[int] = None) -> List[Alert]:
        results = []
        for alert in self.alerts.values():
            if severity and alert.severity != severity:
                continue
            if status and alert.status != status:
                continue
            # Filter by audience
            if audience_user_id is not None:
                if not (alert.visibility_org or
                        audience_user_id in alert.visibility_users or
                        (audience_team_id is not None and audience_team_id in alert.visibility_teams)):
                    continue
            results.append(alert)
        return results

# User Alert Preference Manager
class UserAlertPreferenceManager:
    def __init__(self):
        # key: (user_id, alert_id)
        self.preferences: Dict[(int, int), UserAlertPreference] = {}

    def get_or_create(self, user_id: int, alert_id: int) -> UserAlertPreference:
        key = (user_id, alert_id)
        if key not in self.preferences:
            self.preferences[key] = UserAlertPreference(user_id, alert_id)
        return self.preferences[key]

    def snooze_alert(self, user_id: int, alert_id: int, snooze_date: date):
        pref = self.get_or_create(user_id, alert_id)
        pref.snooze(snooze_date)

    def mark_read(self, user_id: int, alert_id: int):
        pref = self.get_or_create(user_id, alert_id)
        pref.mark_read()

    def mark_unread(self, user_id: int, alert_id: int):
        pref = self.get_or_create(user_id, alert_id)
        pref.mark_unread()

# Notification Service (Observer + Reminder Logic)
class NotificationService:
    def __init__(self, alert_manager: AlertManager,
                 user_pref_manager: UserAlertPreferenceManager,
                 users: List[User ],
                 notification_channels: Dict[DeliveryType, NotificationChannel]):
        self.alert_manager = alert_manager
        self.user_pref_manager = user_pref_manager
        self.users = users
        self.notification_channels = notification_channels
        self.delivery_log: List[NotificationDelivery] = []

    def get_recipients_for_alert(self, alert: Alert) -> List[User ]:
        recipients = []
        for user in self.users:
            if alert.visibility_org:
                recipients.append(user)
            elif user.id in alert.visibility_users:
                recipients.append(user)
            elif user.team.id in alert.visibility_teams:
                recipients.append(user)
        return recipients

    def trigger_reminders(self, current_time: datetime):
        today = current_time.date()
        for alert in self.alert_manager.alerts.values():
            if not alert.is_active(current_time) or not alert.reminders_enabled:
                continue
            recipients = self.get_recipients_for_alert(alert)
            for user in recipients:
                pref = self.user_pref_manager.get_or_create(user.id, alert.id)
                # Check snooze for today
                if pref.is_snoozed_today(today):
                    continue
                # Check if reminder should be sent based on last delivery time
                last_delivery = self._get_last_delivery(alert.id, user.id)
                if last_delivery:
                    next_reminder_time = last_delivery.delivery_time + timedelta(hours=alert.reminder_frequency_hours)
                    if current_time < next_reminder_time:
                        continue
                # Send notification
                channel = self.notification_channels.get(alert.delivery_type)
                if channel:
                    channel.send(user, alert)
                    self.delivery_log.append(NotificationDelivery(alert.id, user.id, current_time))

    def _get_last_delivery(self, alert_id: int, user_id: int) -> Optional[NotificationDelivery]:
        # Return the most recent delivery for alert-user
        deliveries = [d for d in self.delivery_log if d.alert_id == alert_id and d.user_id == user_id]
        if not deliveries:
            return None
        return max(deliveries, key=lambda d: d.delivery_time)

# Analytics Service
class AnalyticsService:
    def __init__(self, alert_manager: AlertManager,
                 user_pref_manager: UserAlertPreferenceManager,
                 delivery_log: List[NotificationDelivery]):
        self.alert_manager = alert_manager
        self.user_pref_manager = user_pref_manager
        self.delivery_log = delivery_log

    def total_alerts_created(self) -> int:
        return len(self.alert_manager.alerts)

    def alerts_delivered_vs_read(self) -> Dict[str, int]:
        delivered = len(self.delivery_log)
        read = 0
        for pref in self.user_pref_manager.preferences.values():
            if pref.state == UserAlertState.READ:
                read += 1
        return {"delivered": delivered, "read": read}

    def snoozed_counts_per_alert(self) -> Dict[int, int]:
        counts = {}
        for pref in self.user_pref_manager.preferences.values():
            if pref.state == UserAlertState.SNOOZED:
                counts[pref.alert_id] = counts.get(pref.alert_id, 0) + 1
        return counts

    def breakdown_by_severity(self) -> Dict[Severity, int]:
        counts = {sev: 0 for sev in Severity}
        for alert in self.alert_manager.alerts.values():
            counts[alert.severity] += 1
        return counts

# Example Seed Data
def seed_data():
    team_eng = Team(1, "Engineering")
    team_marketing = Team(2, "Marketing")

    users = [
        User(1, "Alice", team_eng),
        User(2, "Bob", team_eng),
        User(3, "Charlie", team_marketing),
    ]
    return users, [team_eng, team_marketing]

# Usage Example
if __name__ == "__main__":
    users, teams = seed_data()
    alert_manager = AlertManager()
    user_pref_manager = UserAlertPreferenceManager()
    notification_channels = {
        DeliveryType.IN_APP: InAppChannel()
    }
    notification_service = NotificationService(alert_manager, user_pref_manager, users, notification_channels)

    # Admin creates an alert visible to Engineering team
    alert = alert_manager.create_alert(
        title="System Maintenance",
        message="Scheduled maintenance at midnight.",
        severity=Severity.INFO,
        delivery_type=DeliveryType.IN_APP,
        start_time=datetime.now(),
        expiry_time=datetime.now() + timedelta(days=1),
        visibility_org=False,
        visibility_teams={1},
        visibility_users=None
    )

    # Simulate triggering reminders
    print("\n--- Triggering reminders ---")
    notification_service.trigger_reminders(datetime.now())

    # User snoozes alert
    user_pref_manager.snooze_alert(user_id=1, alert_id=alert.id, snooze_date=datetime.now().date())
    print("\nUser  Alice snoozed the alert for today.")

    # Trigger reminders again (Alice should not get it)
    print("\n--- Triggering reminders again ---")
    notification_service.trigger_reminders(datetime.now())

    # Analytics
    analytics = AnalyticsService(alert_manager, user_pref_manager, notification_service.delivery_log)
    print("\n--- Analytics ---")
    print("Total alerts created:", analytics.total_alerts_created())
    print("Delivered vs Read:", analytics.alerts_delivered_vs_read())
    print("Snoozed counts:", analytics.snoozed_counts_per_alert())
    print("Breakdown by severity:", {k.value: v for k, v in analytics.breakdown_by_severity().items()})
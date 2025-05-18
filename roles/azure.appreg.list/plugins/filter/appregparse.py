from datetime import datetime, timedelta, timezone
import sys
import os
from typing import List, Any
from ansible.utils.unsafe_proxy import AnsibleUnsafeText
from ansible.errors import AnsibleFilterError


from models import AppRegistration, ExpiredApp, ExpiredPasswordCredential

def sanitize(value: Any) -> Any:
    # If it's an AnsibleUnsafeText (or subclass), convert to str
    if isinstance(value, AnsibleUnsafeText):
        return str(value)

    # Recursively sanitize lists
    if isinstance(value, list):
        return [sanitize(v) for v in value]

    # Recursively sanitize dicts
    if isinstance(value, dict):
        return {sanitize(k): sanitize(v) for k, v in value.items()}

    return value

def parse_app_registrations(data: List[dict]) -> List[AppRegistration]:
    print("Parsing app registrations...")
    return [AppRegistration(**app) for app in data]

def apps_with_password(apps):
    return [app for app in apps if len(app.passwordCredentials) > 0]

def filter_by_tag(apps, tag):
    return [app for app in apps if tag in app.get("tags", [])]

def expiring(apps):
    # Get the current date
    now = datetime.now()
    # Calculate the date 30 days from now
    threshold_date = now + timedelta(days=30)
    # Filter apps based on password expiration date
    return [
        app for app in apps if any(
            # Parse 'endDateTime' and convert it to a datetime.date object
            datetime.strptime(cred.get("endDateTime").split('T')[0], "%Y-%m-%d") < threshold_date
            for cred in app.get("passwordCredentials", [])
        )
    ]

def expired(apps: list[AppRegistration]):
    try:
        instances = [AppRegistration(**app) for app in apps]
    except Exception as e:
        raise AnsibleFilterError(f"Failed to convert to AppRegistration: {e}")

    # Get the current date
    now = datetime.now(timezone.utc)
    # Calculate the date 30 days from now
    threshold_date = now + timedelta(days=0)


    print(len(instances[0].passwordCredentials))
    instances = apps_with_password(instances)
    print("Filtered instances without password:")
    print(instances)

    expired_apps = []
    for app in instances:
        expired_credentials = []
        for cred in app.passwordCredentials:
            # Parse 'endDateTime' and convert it to a datetime.date object
            if cred.endDateTime < threshold_date:
                expired_credentials.append(ExpiredPasswordCredential(**cred.model_dump(mode="json")))
        if expired_credentials:
            expired_apps.append(ExpiredApp(
                appId=app.appId,
                displayName=app.displayName,
                expiredCredentials=expired_credentials
            ).model_dump(mode="json"))



    # Filter apps based on password expiration date
    return expired_apps

class FilterModule(object):
    def filters(self):
        return {
            'apps_with_passwords': apps_with_password,
            'filter_by_tag': filter_by_tag,
            'expiring': expiring,
            'expired': expired
        }

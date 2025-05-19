from datetime import datetime, timedelta, timezone
import sys
import os
from typing import List, Any
from ansible.utils.unsafe_proxy import AnsibleUnsafeText
from ansible.errors import AnsibleFilterError


from models import AppRegistration, ExpiredApp, ExpiredPasswordCredential


def convert_AnsibleUnsafeText_to_Model(apps: List[AppRegistration]) -> list[AppRegistration]:
    try:
        instances = [AppRegistration(**app) for app in apps]
    except Exception as e:
        raise AnsibleFilterError(f"Failed to convert to AppRegistration: {e}")

    return [app for app in instances]


def apps_with_password(apps: list[AppRegistration]) -> list[AppRegistration]:
    instances = convert_AnsibleUnsafeText_to_Model(apps)

    return [app.model_dump(mode="json") for app in instances if len(app.passwordCredentials) > 0]


def apps_with_no_passwords(apps: list[AppRegistration]) -> list[AppRegistration]:
    instances = convert_AnsibleUnsafeText_to_Model(apps)

    return [app.model_dump(mode="json") for app in instances if len(app.passwordCredentials) == 0]


def apps_with_incorrect_password_num(apps: list[AppRegistration]) -> list[AppRegistration]:
    instances = convert_AnsibleUnsafeText_to_Model(apps)

    return [app.model_dump(mode="json") for app in instances if (len(app.passwordCredentials) != 1 and len(app.passwordCredentials) != 2)]


def apps_with_long_password_duration(apps: list[AppRegistration]) -> list[AppRegistration]:
    instances = convert_AnsibleUnsafeText_to_Model(apps)
    # Get the current date
    now = datetime.now(timezone.utc)
    # Calculate the date 181 days from now
    threshold_date = now + timedelta(days=181)
    returnapps = []
    for app in instances:
        for password in app.passwordCredentials:
            if password.endDateTime > threshold_date:
                returnapps.append(app)

    return [app.model_dump(mode="json") for app in returnapps]


def filter_by_tag(apps: List[AppRegistration], tag: str) -> List[AppRegistration]:
    instances = convert_AnsibleUnsafeText_to_Model(apps)

    return [app.model_dump(mode="json") for app in instances if tag in app.tags]


def expiring(apps: list[AppRegistration]) -> (list[ExpiredApp] | None):
    instances = convert_AnsibleUnsafeText_to_Model(apps)

    # Get the current date
    now = datetime.now(timezone.utc)

    # Calculate the date 0 days from now
    threshold_date = now + timedelta(days=30)

    expired_apps = []
    # Return app and password credentials together for easier deletion in the module
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


def expired(apps: list[AppRegistration]) -> (list[ExpiredApp] | None):
    instances = convert_AnsibleUnsafeText_to_Model(apps)

    # Get the current date
    now = datetime.now(timezone.utc)

    # Calculate the date 0 days from now
    threshold_date = now + timedelta(days=0)

    # Return app and password credentials together for easier deletion in the module
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


# Any function defined in this file can be used as a filter in Ansible
class FilterModule(object):
    def filters(self):
        return {
            'apps_with_no_passwords': apps_with_no_passwords,
            'apps_with_long_password_duration': apps_with_long_password_duration,
            'apps_with_incorrect_password_num': apps_with_incorrect_password_num,
            'apps_with_passwords': apps_with_password,
            'filter_by_tag': filter_by_tag,
            'expiring': expiring,
            'expired': expired
        }

import requests
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

from models import AppRegistration

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs) -> (list[dict]):
        if not terms:
            raise AnsibleError("Access token required")

        token = terms[0]
        headers = {
            "Authorization": f"Bearer {token}"
        }

        api_url = "https://graph.microsoft.com/v1.0/applications"

        try:
            api_response = requests.get(
                api_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            api_response.raise_for_status()
            apps = api_response.json().get("value", [])
            myapps = []
            for app in apps:
                # Unpack the app dictionary into the pydantic AppRegistration model
                app_reg = AppRegistration(**app)
                myapps.append(app_reg)

            # Convert pydantic models to json
            return [app.model_dump(mode="json") for app in myapps]

        except Exception as e:
            raise AnsibleError(f"Failed to call API: {e}")
            return []

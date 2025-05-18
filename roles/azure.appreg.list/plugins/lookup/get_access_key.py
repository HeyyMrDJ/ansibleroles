import os
import requests
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        # 1. Load environment variables
        token_url = os.environ.get('OAUTH_URL')
        client_id = os.environ.get('OAUTH_CLIENTID')
        client_secret = os.environ.get('OAUTH_SECRET')
        scope = os.environ.get('OAUTH_SCOPE')

        if not all([token_url, client_id, client_secret, scope]):
            raise AnsibleError("Missing one or more required environment variables.")

        # 2. Get access token using requests
        try:
            response = requests.post(
                token_url,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": scope,
                    "grant_type": "client_credentials"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            token = response.json()["access_token"]

        except Exception as e:
            raise AnsibleError(f"Failed to get access token: {e}")

        return [token.strip()]

#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
__metaclass__ = type
from ansible.errors import AnsibleError
import requests

DOCUMENTATION = r'''
---
module: delete_appreg_secret

short_description: A module for deleting app registration secrets.

version_added: "1.0.0"

description: A module that deletes app registration secrets.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: dict
author:
    - DJ (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  appreg-delete-secret:
    name: apps
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='dict', required=True),
        token=dict(type='str', required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    print(module.params['name']['appId'])
    keyId = module.params['name']['expiredCredentials'][0]['keyId']
    id = module.params['name']['appId']
    token = module.params['token'].strip()
    delete_expired_secrets(token, id, keyId)


    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['original_message'] = module.params['name']
    result['message'] = "goodbye"

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def delete_expired_secrets(token, id, keyId):
    """TEST"""
    print("Checking vars")
    print(f"ID: {id}")
    print(f"KeyId: {keyId}")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 3. Call the hardcoded API
    api_url = f"https://graph.microsoft.com/v1.0/applications(appId='{id}')/removePassword"
    token = token.strip()

    try:
        api_response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "keyId": keyId,
            }
        )
        api_response.raise_for_status()
        return []
    except Exception as e:
        raise AnsibleError(f"Failed to call API: {e}")


def main():
    run_module()


if __name__ == '__main__':
    main()

import base64
import requests
import json
from datetime import datetime as dt


# Configs
TOKEN = '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'
REPO_OWNER = 'emad-mohamadi'
REPO_NAME = 'data-server'
GLOBAL_FILE_PATH = 'global.json'
LOCAL_FILE_PATH = 'local.json'
BRANCH = 'main'
URL = f'https://api.github.com/repos/{REPO_OWNER}/{
    REPO_NAME}/contents/{GLOBAL_FILE_PATH}?ref={BRANCH}'
HEADERS = {
    'Authorization': f'token {TOKEN}',
    # 'Accept': 'application/vnd.github.v3+json'
}


class Data:
    def __init__(self, id=None, local_path="local.json"):
        self.id = id
        self.global_data = None
        self.local_data = None
        return

    def read_global_data(self):
        """
        Reads the global data.
        """
        try:
            # Get data
            response = requests.get(URL, headers=HEADERS)
            response.raise_for_status()
            content = response.json()
            file_content = content['content']
            self.file_sha = content['sha']

            # Decode content
            decoded_content = base64.b64decode(file_content).decode('utf-8')
            self.global_data = json.loads(decoded_content)
        except:
            return False

        return True

    def write_global_data(self):
        """
        Updates the global data.
        """
        try:
            # Encode content
            updated_content = base64.b64encode(json.dumps(
                self.global_data).encode('utf-8')).decode('utf-8')

            # Update data
            update_url = f'https://api.github.com/repos/{
                REPO_OWNER}/{REPO_NAME}/contents/{GLOBAL_FILE_PATH}'
            update_data = {
                'message': f'<{self.id}>-<{dt.now()}>',
                'content': updated_content,
                'sha': self.file_sha,
                'branch': BRANCH
            }
            update_response = requests.put(
                update_url, headers=HEADERS, json=update_data
            )
            update_response.raise_for_status()
        except:
            return False

        return True

    def read_local_data(self):
        with open(LOCAL_FILE_PATH, "r") as local:
            self.local_data = json.load(local)


data = Data()
data.read_global_data()
with open("local.json", "r") as file:
    data.global_data = json.load(file)
data.write_global_data()

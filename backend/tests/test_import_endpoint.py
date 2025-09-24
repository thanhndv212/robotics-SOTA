import requests
import os

BASE = os.environ.get('BASE_URL', 'http://127.0.0.1:8080')

def run_import_test():
    url = f"{BASE}/api/papers/import"
    files = {'file': open('backend/tests/sample_import.csv', 'rb')}
    params = {'insert': 'false'}
    resp = requests.post(url, files=files, params=params, timeout=10)
    print('Status:', resp.status_code)
    try:
        print('JSON:', resp.json())
    except Exception:
        print('Text:', resp.text)

if __name__ == '__main__':
    run_import_test()

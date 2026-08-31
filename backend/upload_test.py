import requests
import time
import sys
import os

def upload():
    url = "http://127.0.0.1:8000/api/upload"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_data", "dataset.csv")

    if not os.path.exists(file_path):
        print(f"Dataset not found at {file_path}")
        print("Run: python demo_data/generate_dataset.py")
        return

    # Wait for server to boot
    print("Waiting for server...")
    for _ in range(30):
        try:
            res = requests.get("http://127.0.0.1:8000/")
            if res.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)

    print(f"Uploading {file_path}...")
    with open(file_path, "rb") as f:
        files = {"file": ("dataset.csv", f, "text/csv")}
        response = requests.post(url, files=files)

    print(f"Status: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    upload()

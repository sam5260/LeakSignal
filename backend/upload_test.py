import requests
import time
import sys

def upload():
    url = "http://127.0.0.1:8000/api/upload"
    file_path = "C:/Users/paras/Downloads/LeakSignal/backend/demo_data/dataset.csv"
    
    # Wait for server to boot
    for _ in range(30):
        try:
            res = requests.get("http://127.0.0.1:8000/")
            if res.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
            
    print("Uploading dataset...")
    with open(file_path, "rb") as f:
        files = {"file": ("dataset.csv", f, "text/csv")}
        response = requests.post(url, files=files)
        
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    upload()

import requests
import json

def test_erail():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    urls = [
        "https://erail.in/data.aspx?Action=TRAINROUTE&TrainNo=12952",
        "https://erail.in/rail/getTrains.aspx?TrainNo=12952&DataSource=0&Language=0&Cache=true"
    ]

    for url in urls:
        print(f"\nFetching {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print("Status:", response.status_code)
            print("Content (first 200 chars):", repr(response.text[:200]))
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    test_erail()

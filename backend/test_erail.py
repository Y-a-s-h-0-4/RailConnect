import requests

def test_erail():
    url = "https://erail.in/rail/getTrains.aspx?Station_From=NDLS&Station_To=BCT"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Response Content Length:", len(response.text))
    print("Sample:", response.text[:1000])

if __name__ == "__main__":
    test_erail()

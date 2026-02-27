import requests

def test_erail_trains():
    url = "https://erail.in/data.aspx?Action=TRAINBETWEENSTATIONS&StationFrom=NDLS&StationTo=BCT&DataSource=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        print("BETWEEN STATIONS Status:", response.status_code)
        print("BETWEEN STATIONS Sample:", response.text[:500])
    except Exception as e:
        print("BETWEEN STATIONS Error:", e)

    url2 = "https://erail.in/data.aspx?Action=TRAINROUTE&TrainNo=12952"
    try:
        response = requests.get(url2, headers=headers)
        print("ROUTE Status:", response.status_code)
        print("ROUTE Sample:", response.text[:500])
    except Exception as e:
        print("ROUTE Error:", e)

    url3 = "https://erail.in/rail/getTrains.aspx?TrainNo=12952&DataSource=0&Language=0&Cache=true"
    try:
        response = requests.get(url3, headers=headers)
        print("TRAIN DETAILS Status:", response.status_code)
        print("TRAIN DETAILS Sample:", response.text[:500])
    except Exception as e:
        print("TRAIN DETAILS Error:", e)

if __name__ == "__main__":
    test_erail_trains()

import json
import ssl
import urllib.request

c=ssl._create_unverified_context()
res = urllib.request.urlopen("https://raw.githubusercontent.com/datameet/railways/master/schedules.json", context=c)
data = json.loads(res.read())

t_47154 = [d for d in data if d["train_number"] == "47154"]
t_47154.sort(key=lambda x: x["id"])

print(f"Stops for 47154: {len(t_47154)}")
for i, d in enumerate(t_47154[:10]):
    print(f"{i}: {d['station_code']}, arr: {d['arrival']}, dep: {d['departure']}, id: {d['id']}")

import urllib.request
import json
import ssl

c=ssl._create_unverified_context()
res = urllib.request.urlopen("https://raw.githubusercontent.com/datameet/railways/master/schedules.json", context=c)
data = json.loads(res.read())
print(json.dumps(data[:5], indent=2))

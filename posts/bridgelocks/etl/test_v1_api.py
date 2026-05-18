import urllib.request
import ssl
import json

TOKEN = "AAAAAAAAAAAAAAAAAAAAAJ250AEAAAAA6%2FHfrZ%2Fq2XonElgjMCNRVWt2WLw%3DF23TJKfi9SPrU233ojDjzOz9IpthDEQnFVjXVQu76yzUJpVzTI"

url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=SDOTbridges&count=10"
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {TOKEN}')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Success! Fetched", len(data), "tweets.")
        if data:
            print(data[0].get('text'))
            print(data[0].get('created_at'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
    print(e.read().decode('utf-8'))

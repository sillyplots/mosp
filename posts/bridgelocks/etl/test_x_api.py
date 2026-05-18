import urllib.request
import ssl
import json

TOKEN = "AAAAAAAAAAAAAAAAAAAAANyj9gEAAAAAcwMMh9OD%2B6UBAbmY0NJWGWwrRTE%3D75MkjEqkRxvnyWsshB3ntKBZRYsF42ryMipvAkjfQoVxWK9fey"

# Test v2 API endpoint for user lookup
url = "https://api.twitter.com/2/users/by/username/SDOTbridges"
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {TOKEN}')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Success!", data)
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
    print(e.read().decode('utf-8'))

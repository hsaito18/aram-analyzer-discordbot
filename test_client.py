import requests
import base64

SERVER_URL = 'http://localhost:5900'

r = requests.get(f'{SERVER_URL}/graphics/player-stats/33opo/0033')

imgdata = base64.b64decode(r.text)
filename = 'test.jpeg'
with open(filename, 'wb') as f:
  f.write(imgdata)

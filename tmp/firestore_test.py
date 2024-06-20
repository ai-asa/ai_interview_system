# %%
import requests
import json

def send_data_to_gas(user_id, status):
    url = 'https://script.google.com/macros/s/AKfycbwsnn2Yo22alu5FVmi81sF5jCFTeUUpI1p8WG12r2WWcewPz4zSIvie8KxrxHB5d2kb/exec'
    headers = {'Content-Type': 'application/json'}
    data = {
        'user_id': user_id,
        'message': status
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.text)

# データを送信する例
send_data_to_gas('testtest', '1')

# %%

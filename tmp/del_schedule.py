# %%
import requests

def send_event_data(userId, eventDate):
    # GASのWebアプリケーションのURL
    url = "https://script.google.com/macros/s/AKfycbwFzDgrpl7R1_abhaQKfz9V4Vjv1ETR5wSSM_GmTFGn3z3_tAEumEOg7RDETwc4ICcQ/exec"

    # 送信するデータ
    data = {
        'userId': userId,
        'eventDate': eventDate
    }

    # HTTP POSTリクエストを送信
    response = requests.post(url, data=data)

    # レスポンスの内容を表示
    print(response.text)

# 使用例
userId = 'example_user_id'
eventDate = '2024070515'  # YYYYMMDDHHの形式
send_event_data(userId, eventDate)

# %%

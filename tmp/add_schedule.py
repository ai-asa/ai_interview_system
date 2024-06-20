# %%
import requests

def send_event_to_gas(userId, eventDate):
    # GASのWebアプリケーションのURL
    url = "https://script.google.com/macros/s/AKfycbxoKRcEx_-kTo46Xk0aXuTtItGJUju9JvDsOEFeQgdshXUa0JudZXEG2O63phokzRTD8w/exec"
    
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
userId = 'your_user_id'
eventDate = '2024070515'  # YYYYMMDDHHの形式
send_event_to_gas(userId, eventDate)


# %%

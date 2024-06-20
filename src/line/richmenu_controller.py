# %%
import os
from dotenv import load_dotenv
import configparser
import requests
import json

class RichmenuController:
    load_dotenv()
    LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
    config = configparser.ConfigParser()
    config.read('config.txt')
    richMenuIds_path = config.get('DATA', 'richmenu_ids_path', fallback="./data/richmenu/ids/ids.json")
    rich_Image_path = config.get('DATA', 'richmenu_image_path', fallback="./data/richmenu/images/")

    def __init__(self):
        if not os.path.exists(self.richMenuIds_path):
            self.gen_richmenu_all()
        with open(self.richMenuIds_path,'r') as f:
            self.richMenuIds = json.load(f)
        pass
    
    def gen_richmenu_all(self):
        data_list = []
        data_1= {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": False,
            "name": "richmenu1",
            "chatBarText": "Menu",
            "areas": [
                {
                    "bounds": {
                        "x": 0,
                        "y": 0,
                        "width": 1250,
                        "height": 1686
                    },
                    "action": {
                        "type": "postback",
                        "data": "richmenu1",
                        "displaytext":"面接をご希望いただきありがとうございます！\n\nこのあと送信される\n「技術者採用エントリーフォーム」に必要事項をご記入ください。\n現在フォームを作成しています..."
                    }
                },
                # 他のエリアの定義もここに追加可能
            ]
        }
        data_list.append(data_1)
        data_2= {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": False,
            "name": "richmenu2",
            "chatBarText": "Menu",
            "areas": [
                {
                    "bounds": {
                        "x": 0,
                        "y": 0,
                        "width": 1250,
                        "height": 1686
                    },
                    "action": {
                        "type": "postback",
                        "data": "richmenu2",
                        "displaytext":"エントリーフォームの入力を完了いただきありがとうございます。\n以降は変更・修正を受け付けませんのでご了承ください。\n\nエントリーフォームにご記入いただいた電話番号宛に、\n本人確認用のSMS認証コードを送信いたします。\n認証コードを受信しましたら、\n6桁の半角英数字の認証コードを\nこのトークに送信してください。\n\n※テキストボックスの表示方法\n →画面左下のキーボードマークをタップ"
                    }
                },
            ]
        }
        data_list.append(data_2)
        data_3= {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": False,
            "name": "richmenu3",
            "chatBarText": "Menu",
            "areas": [
                {
                    "bounds": {
                        "x": 0,
                        "y": 0,
                        "width": 1250,
                        "height": 1686
                    },
                    "action": {
                        "type": "postback",
                        "data": "richmenu3",
                        "displaytext":"面接予定日を確認しています..."
                    }
                },
            ]
        }
        data_list.append(data_3)
        data_4= {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": False,
            "name": "richmenu4",
            "chatBarText": "Menu",
            "areas": [
                {
                    "bounds": {
                        "x": 0,
                        "y": 0,
                        "width": 1250,
                        "height": 1686
                    },
                    "action": {
                        "type": "postback",
                        "data": "richmenu4",
                        "displaytext":"面接に関する情報を取得しています..."
                    }
                },
            ]
        }
        data_list.append(data_4)
        parts = []
        for i in range(len(data_list)):
            richmenu_id = self._gen_richmenu(data_list[i],self.rich_Image_path + f"{i}" + ".png")
            part = {
                "richMenu_Num":i+1,
                "richMenu_Id":richmenu_id
            }
            parts.append(part)
        with open(self.richMenuIds_path, 'w') as f:
            json.dump(parts, f)
        pass

    def _gen_richmenu(self,data,image_path):
        headers = {
            'Authorization': f'Bearer {self.LINE_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        response = requests.post('https://api.line.me/v2/bot/richmenu', 
                                 headers=headers, 
                                 data=json.dumps(data))
        response_json = response.json()
        print(response_json)
        richmenu_id = response_json.get("richMenuId")
        self._upload_image(richmenu_id,image_path)
        return richmenu_id

    def _upload_image(self,richmenu_id,image_path):
        headers = {
            'Authorization': f'Bearer {self.LINE_ACCESS_TOKEN}',
            'Content-Type': 'image/png'
        }
        with open(image_path, 'rb') as f:
            response = requests.post(f'https://api-data.line.me/v2/bot/richmenu/{richmenu_id}/content', 
                                     headers=headers, 
                                     data=f)
            print(response.status_code, response.reason)
            print(response.text)

    def change_richmenu_user(self,rich_num,user_id):
        for richMenuId in self.richMenuIds:
            if richMenuId["richMenu_Num"] == rich_num:
                rich_id = richMenuId["richMenu_Id"]
        try:
            response = requests.post(f'https://api.line.me/v2/bot/user/{user_id}/richmenu/{rich_id}', 
                                    headers={'Authorization': f'Bearer {self.LINE_ACCESS_TOKEN}'})
            print(response.status_code, response.reason)
            print(response.text)
        except:
            print("richMenuIdが見つかりません。")
        pass

    def change_richmenu_all(self,rich_num):
        for richMenuId in self.richMenuIds:
            if richMenuId["richMenu_Num"] == rich_num:
                rich_id = richMenuId["richMenu_Id"]
        try:
            response = requests.post(f'https://api.line.me/v2/bot/user/all/richmenu/{rich_id}', 
                                    headers={'Authorization': f'Bearer {self.LINE_ACCESS_TOKEN}'})
            print(response.status_code, response.reason)
            print(response.text)
        except:
            print("richMenuIdが見つかりません。")
        pass

if __name__ == "__main__":
    rt = RichmenuController()
    #rt.gen_richmenu_all()
    rt.change_richmenu_all(1)

# %%

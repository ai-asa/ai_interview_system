# %%
import obsws_python as obs
import os
from dotenv import load_dotenv

class OBSAdapter:
    
    def __init__(self) -> None:
        load_dotenv()
        password = os.environ.get('OBS_WS_PASSWORD')
        host = os.environ.get('OBS_WS_HOST')
        port = os.environ.get('OBS_WS_PORT')
        # 設定されていない場合はエラー
        if(password == None or host == None or port == None):
            raise Exception("OBSの設定がされていません")
        self.ws = obs.ReqClient(host=host, port=port, password=password)
    
    def set_subtitle_ditect(self, text:str):
        self.ws.set_input_settings(name="Ditect", settings={"text":text},overlay=True)

    def set_subtitle_ai(self, text:str):
        self.ws.set_input_settings(name="AI", settings={"text":text},overlay=True)
    
    def set_subtitle_explain1(self, text:str):
        self.ws.set_input_settings(name="Explain1", settings={"text":text},overlay=True)

    def set_subtitle_explain2(self, text:str):
        self.ws.set_input_settings(name="Explain2", settings={"text":text},overlay=True)

if __name__=='__main__':
    obsAdapter = OBSAdapter()
    import random
    text = "Questionの番号は" + str(random.randint(0,100))
    obsAdapter.set_subtitle_question(text)
            

# %%

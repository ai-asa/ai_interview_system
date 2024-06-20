# %%
import configparser
from io import BytesIO
from openai import OpenAI
import os
import re
import speech_recognition as sr
import librosa
import numpy as np
import whisper
from src.obs.obs_websocket_adapter import OBSAdapter

class WhisperApiAdapter:

    client = OpenAI()#なんかopenai key入れなくても動くんだけど...（恐怖） api_key=os.getenv('OPENAI_API_KEY')
    config = configparser.ConfigParser()
    config.read('config.txt')
    device_list_path = config.get('CONFIG', 'device_list_path', fallback='./device_list.txt')
    device_name = config.get('CONFIG', 'device_name', fallback='Hi-Fi Cable Output (VB-Audio Hi')
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.energy_threshold = 500
    r.pause_threshold = 1
    default_device = None
    ob = OBSAdapter()

    def __init__(self):
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if name == self.device_name:
                self.default_device = index
                break
        if self.default_device is None:
            print("指定のdevice_nameが見つかりませんでした")
            exit()
        pass

    def get_device_list(self):
        text_list = []
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            text_list.append(f"Microphone with name \"{name}\" found for `Microphone(device_index={index})`")
            text = "\n".join(text_list)
        with open(self.device_list_path,"w",encoding="utf-8") as f:
            f.write(text)
    
    def _recoding(self):
        """
        読み取りの際のパラメータをもっと細かく指定したい
        """
        with sr.Microphone(device_index=self.default_device, sample_rate=44100) as source:
            #self.r.adjust_for_ambient_noise(source, duration=1)
            print("音声認識中")
            self.ob.set_subtitle_ditect("【聞き取り中...】")
            audio = self.r.listen(source,timeout=None,phrase_time_limit=30)
            print("音声取得完了")
            self.ob.set_subtitle_ditect("【処理中...】")
        self.audio_file = BytesIO(audio.get_wav_data())
        self.audio_file.name = "from_mic.wav"

        #with open("recorded_audio.wav", "wb") as f:
        #    f.write(audio.get_wav_data())
    
    def _transcript(self,option=0):
        if option == 0:
            prompt = "発言者が「回答します」と言ったかどうかを判断します。"
        elif option == 1:
            prompt = "面接者が面接官からの質問に答えています。"
        elif option == 2:
            prompt = "2人の人物が会話をしています。"
        transcription = self.client.audio.transcriptions.create(
            file=self.audio_file,
            model="whisper-1",
            language="ja",
            response_format="text",
            #temperature = 1,
            prompt = prompt
            )
        return transcription
    
    def detect_wakeup_word(self):
        self._recoding()
        transcription = self._transcript(option=0)
        match = re.search(r"回答|かいとう",transcription)
        if match:
            return True
        else:
            return False

    def detect_audio(self,option=0):
        self._recoding()
        transcription = self._transcript(option)
        return transcription
        
if __name__ == "__main__":
    wa = WhisperApiAdapter()
    #wa.get_device_list()
    print(wa.detect_audio())

# %%

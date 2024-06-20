# %%
import configparser
from dotenv import load_dotenv
from openai import OpenAI
import os

class OpenaiAdapter:

    load_dotenv()
    config = configparser.ConfigParser()
    config.read('config.txt')
    retry_limit = int(config.get('CONFIG', 'retry_limit', fallback=5))

    def __init__(self):
        self.client = OpenAI(
            api_key = os.getenv('OPENAI_API_KEY')
        )
    
    def openai_chat(self, openai_model, prompt, temperature=1):
        system_prompt = [{"role": "system", "content": prompt}]
        for i in range(self.retry_limit):
            try:
                response = self.client.chat.completions.create(
                    messages=system_prompt,
                    model=openai_model,
                    temperature=temperature
                )
                text = response.choices[0].message.content
                return text
            except Exception as error:
                print(f"GPT呼び出し時にエラーが発生しました:{error}")
                if i == self.retry_limit - 1:
                    return None  # エラー時はNoneを返す
                continue
    
    def openai_chat_streaming(self, openai_model, prompt, temperature=1):
        system_prompt = [{"role": "system", "content": prompt}]
        for i in range(self.retry_limit):
            try:
                stream = self.client.chat.completions.create(
                    model=openai_model,
                    messages=system_prompt,
                    temperature=temperature,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                break
            except Exception as error:
                print(f"GPT呼び出し時にエラーが発生しました:{error}")
                if i == self.retry_limit - 1:
                    return None  # エラー時はNoneを返す
                continue

if __name__ == "__main__":
    oa = OpenaiAdapter()
    for text_chunk in oa.openai_chat_streaming("gpt-4-0125-preview", "桃太郎の物語を教えて下さい", temperature=0.7):
        print(text_chunk + "\n")
# %%

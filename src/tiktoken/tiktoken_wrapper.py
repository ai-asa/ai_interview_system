import tiktoken
class tiktoken_wrapper:

    def __init__(self):
        pass

    def token_counter(self, openai_model, text) -> int:
        if openai_model == {"text-embedding-ada-002" or "gpt-3.5-turbo" or "gpt-3.5-turbo-1106" or "gpt-3.5-turbo-16k" or "gpt-4" or "gpt-4-1106-preview"}:
            tokenizer_model = "cl100k_base"
        elif openai_model == {"text-davinci-002" or "text-davinci-003"}:
            tokenizer_model = "p50k_base"
        elif openai_model == "davinci":
            tokenizer_model = "r50k_base"
        else:
            tokenizer_model = "cl100k_base"
        enc = tiktoken.get_encoding(tokenizer_model)
        token_count = len(enc.encode(text))
        return token_count
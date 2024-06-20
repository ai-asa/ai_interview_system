from dotenv import load_dotenv
import os
import json
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

class query_adapter:
    
    def __init__(self):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    def _load_index(self,index_path,a_path):
        embeddings = OpenAIEmbeddings(openai_api_key=self.OPENAI_API_KEY)
        faiss_index = FAISS.load_local(index_path, embeddings)
        with open(a_path, 'r', encoding='UTF-8') as f:
            a_document = json.load(f)
        return faiss_index, a_document
    
    def query_index(self,query,index_path,a_path):
        faiss_index, a_document = self._load_index(index_path,a_path)
        docs = faiss_index.similarity_search_with_score(query, k=10)
        # idでa文書を検索
        qa_list = []
        q_page_content = ""
        for item in docs:
            q_page_content = item[0].page_content
            id = item[0].metadata['id']
            a_page_content = ""
            for a_text in a_document:
                if a_text['id'] == id:
                    a_page_content = a_text['page_content']
                    break
            if q_page_content and a_page_content:
                qa_list.append(f"Q: {q_page_content}")
                qa_list.append(f"A: {a_page_content}")
        return qa_list
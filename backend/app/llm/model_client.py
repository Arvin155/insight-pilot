from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI

from app.core.config import settings


def get_model_client(api_key=settings.dashscope_api_key, base_url=settings.llm_base_url
                     , model=settings.chat_model, temperature=0.7, max_tokens=8000):
    """通过LangChain获得一个阿里通义千问聊天模型的实例"""
    return ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=temperature, max_tokens=max_tokens)


def get_embeddings():
    """通过LangChain获得一个阿里通义千问嵌入模型的实例"""
    return DashScopeEmbeddings(model=settings.embedding_model, dashscope_api_key=settings.dashscope_api_key)

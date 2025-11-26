try:
    from langchain_ollama import OllamaEmbeddings,ChatOllama
except:
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.chat_models import ChatOllama

from common.utils import read_key
from langchain_core.messages import SystemMessage,HumanMessage

llmcall_msg = """
# 角色 
你是一位卓越的{role}。

## 技能
{skill}

## 限制
- {limit}
- 严格按照“技能”中的“执行”去执行。

## 例子
{example}
"""



def ModelOllama(key_path="configs/ollama.key"):
        key_api = read_key(key_path)
    
        if key_api.get("temperature"):
            chat = ChatOllama(base_url=key_api['url'],model=key_api['chat_n'],temperature=float(key_api["temperature"]))
        else:
            chat = ChatOllama(base_url=key_api['url'],model=key_api['chat_n'])
        return chat
    
  
    
    
def llm_call_f(user_query:str,skill:str,role:str="",limit:str="",example:str=""):
    """
    step_line  <--  system_msg
    content    <--  human_msg
    """
    system_msg = SystemMessage(llmcall_msg.format(skill=skill,example=example,limit=limit,role=role))
    human_msg = HumanMessage(user_query)
    msg = {"SystemMessage":system_msg,"HumanMessage":human_msg}
    chat_m= ModelOllama()
    out = chat_m.invoke(msg).content
    try:
        out = eval(out)
        return out
    except:
        return out
    
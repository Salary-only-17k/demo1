import os
try:
    from langchain_community.vectorstores import Chroma
except:
    from langchain.vectorstores import Chroma
    
from langchain_core.documents import Document

class FileStore(object):
    def __init__(self,colt:str,chroma_dir:str):
        self.colt = colt
        self.chroma_dir = chroma_dir
        self._set_embed = None
        

    def _init_chroma(self):
        if os.path.exists(self.chroma_dir):
            self.chroma_client = Chroma(
                embedding_function=self._set_embed, 
                collection_name=self.colt,
                persist_directory=self.chroma_dir
                )
            start_id = self.chroma_client._collection.count()
            start_tm = self.chroma_client
        else:
            self.chroma_client = Chroma(
                embedding_function=self._set_embed, 
                collection_name=self.colt,
                persist_directory=self.chroma_dir
                )
            start_id = 0
            start_tm = 0
        return start_id
    def update(self,documents:list[Document],ids:list):
        if len(documents) != len(ids):
            raise ValueError("documents和ids列表长度必须一致")

        existing_ids = set()
        if ids:
            existing_data = self.chroma_client.get(ids=ids)
            existing_ids = set(existing_data['ids'])
        
        update_docs = []
        update_ids = []
        add_docs = []
        add_ids = []
        
        for doc, doc_id in zip(documents, ids):
            if doc_id in existing_ids:
                update_docs.append(doc)
                update_ids.append(doc_id)
            else:
                add_docs.append(doc)
                add_ids.append(doc_id)
        
        # 执行更新和新增
        if update_docs:
            self.chroma_client.update_documents(
                documents=update_docs,
                ids=update_ids
            )
        if add_docs:
            self.chroma_client.add_documents(
                documents=add_docs,
                ids=add_ids
            )
        
        self.chroma_client.persist()
        
    def add(self,documents:list[Document],ids:list=None):
        if ids and len(documents) != len(ids):
            raise ValueError("documents和ids列表长度必须一致")
        if ids:
            _ = self.chroma_client.add_documents(documents=documents,ids=ids)
        else:
            _ = self.chroma_client.add_documents(documents=documents)
        self.chroma_client.persist()
        
    
    def delete(self,ids:list[str]):
        self.chroma_client.delete(ids=ids)
        self.chroma_client.persist()
        
    def search(self,query:str,filter_rule:dict[list]=None,top_k:int=5):
        matching_docs = self.chroma_client.similarity_search(
                query=query,
                k=top_k,
                filter=filter_rule)
        return matching_docs
    
    def get(self,ids_lst:list[str]=None,include_info:list[str]=None,where_info:dict=None):
        try:
            return self.chroma_client.get(ids=ids_lst,include=include_info,where=where_info)
        except:
            return None    
from threading import Thread

from core.moudle import receive_thread,infer_thread,aiagent_thread
from core.share_data import audio_queue

    

class pipeline():
    def __init__(self):
        self.receive_thread = Thread(target=receive_thread,name="receive_thread")
        self.infer_thread= Thread(target=infer_thread,name="infer_thread")
        self.aiagent_thread= Thread(target=aiagent_thread,name="aiagent_thread")
    def loop(self):
        threads = [self.receive_thread,self.infer_thread,self.aiagent_thread]
        
        for thread_ in threads:
            thread_.start()
        for thread_ in threads:
            thread_.join()
        print(audio_queue)
  
  
  
if __name__ == "__main__":
    func = pipeline()
    func.loop()
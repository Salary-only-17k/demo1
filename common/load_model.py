import torch

from core.share_data import models_params


    
# class inferBase():
#     def __init__(self):
#         from net.define_model import AudioClassifier
#         self.model = AudioClassifier(2)
#         # print(f">>   {models_params.model_path}")
#         state_dct = torch.load(models_params.model_path, map_location='cpu')
#         self.model.load_state_dict(state_dct)
        
#         self.model.eval()
        
#         # self.model = torch.load(models_params.model_path, map_location='cpu')
#         # self.model.eval()
#     def predict(self,tensor):
#         with torch.no_grad():
#             out = self.model(tensor)
#         return out.cpu().numpy()
class inferBase():
    def __init__(self):
        from net.define_model import AudioClassifier
        self.model = AudioClassifier(2)
        # print(f">>   {models_params.model_path}")
        state_dct = torch.load(models_params.model_path, map_location='cpu')
        self.model.load_state_dict(state_dct["weights"])
        self.labels = state_dct["labels"]
        self.model.eval()
        
        # self.model = torch.load(models_params.model_path, map_location='cpu')
        # self.model.eval()
    def predict(self,tensor):
        with torch.no_grad():
            outs = self.model(tensor)
            tmp = []
            for out in outs:
                tmp.append(self.labels[out.argmax().item()])
            return tmp
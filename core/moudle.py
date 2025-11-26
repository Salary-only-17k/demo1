import torch
import threading
import pathlib
import tqdm
import numpy as np
import fastapi
import cv2
from core.share_data import audio_queue,results_queue,llm_anasys_results_queue, \
                        audio_params,run_params,img_params
from common.cope_audio import cope_audio
from common.load_model import inferBase
from common.llm_api import llm_call_f

def receive_cv_thread():
    if run_params.mode == "test":

        img_paths_lst = list(pathlib.Path(img_params.img_pth).glob("*.jpg"))
        for img_path in tqdm.tqdm(img_paths_lst):
            img_tensor = cv2.imread(img_path)
            # audio_queue.put(wav_tensor)
            #TODO
    
    
def receive_thread():
    print("start Reveive")
    if run_params.mode == "test":
        import torchaudio
        wav_paths_lst = list(pathlib.Path(audio_params.wav_dir).glob("*.wav"))
        for wav_path in tqdm.tqdm(wav_paths_lst):
            wav_tensor,rate = torchaudio.load(wav_path)
            audio_queue.put(wav_tensor)
            # print(">>rate   ",rate)
   
    else:
        import pyaudio
        # 参数设置
        FORMAT = pyaudio.paInt16  # 音频格式 [citation:1][citation:3][citation:9]
        CHANNELS = audio_params.CHANNELS              # 单声道 [citation:3][citation:9]
        RATE = audio_params.RATE              # 采样率 [citation:3]
        CHUNK = audio_params.CHUNK             # 每次读取的帧数 [citation:3][citation:9]
        RECORD_SECONDS = audio_params.RECORD_SECONDS        # 录制时间
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

        previous_wav = None
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            # 从麦克风读取数据 [citation:3][citation:9]
            data = stream.read(CHUNK)
            # 将二进制字符串转换为numpy数组 [citation:9]
            # 使用np.frombuffer将数据转换为16位整数数组
            audio_np = np.frombuffer(data, dtype=np.int16)
            
            # 将numpy数组转换为PyTorch Tensor [citation:10]
            audio_tensor = torch.from_numpy(audio_np.copy()).float()  # 转换为float32
            
            # 归一化到[-1, 1]范围 (适用于16位PCM) [citation:1]
            audio_tensor = audio_tensor / 32768.0
            # 重叠控制
            if previous_wav==None:
                audio_queue.put(audio_tensor)
                previous_wav = audio_tensor
            else:
                num = int(previous_wav.shape.numel()*0.2)
                audio_tensor[0:num] = previous_wav[-num:]
                previous_wav = audio_tensor
            print("录制结束")
        # 关闭流和PyAudio [citation:3][citation:9]
        stream.stop_stream()
        stream.close()
        p.terminate()


def infer_thread():
    print("Start Displaying")
    cope_data_func = cope_audio()
    infer_func = inferBase()
    while True:
        if audio_queue.empty() !=True:
            wav_tensor=audio_queue.get()
            data = cope_data_func.run(wav_tensor)
            out = infer_func.predict(data)
            results_queue.put(out)
            

def aiagent_thread():
    print("Start aiagent")
    while True:
        if results_queue.empty() !=True:
            outs = results_queue.get()
            outs = llm_call_f(user_query=f"需要总结的内容 {outs}",skill="""- 理解异常音频检测结果，红外检测结果。
                                                                         - 结合历史维修记录，维修人等信息，生成分析结果。
                                                                         """,role="工业异常分析专家",limit="""按照格式返回结果
                                                                         {"维修记录",
                                                                         "维修对接人",
                                                                         "设备信息",
                                                                             }""")
            llm_anasys_results_queue.get(outs)
            print(">> out  <>",outs)
            



def color_image_detection_thread(img:str=None):
    #TODO 实现对彩色图像的检测，返回检测结果（id）
    return "id-1"


def (img:str=None):
    #TODO 实现对红外图像的检测，返回检测结果（id）
    return "泵前方拐角处温度异常"

# TODO  infer_thread color_image_detection_thread infrared_image_detection_thread 写成一个thread

def post_thread():
    while True:
        if llm_anasys_results_queue.empty() !=True:
            outs = results_queue.get()
            #TODO 定义后端 fastapi
            print(outs)
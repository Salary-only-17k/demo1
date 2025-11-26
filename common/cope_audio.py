import torchaudio
# import torchaudio.transforms as T
import torch
import numpy
from core.share_data import audio_params,models_params
from common.load_model import inferBase

# mel_spectrogram = T.MelSpectrogram(
#     sample_rate=int(audio_params.sample_rate),  # 与你的音频文件采样率一致[citation:1]
#     n_fft=int(audio_params.n_fft),         # FFT窗口大小
#     hop_length=int(audio_params.hop_length),     # 帧移
#     n_mels=int(audio_params.n_mels),          # 梅尔滤波器数量
#     f_min=int(audio_params.f_min),           # 最小频率
#     f_max=int(audio_params.f_max),         # 最大频率，鉴于采样率为16kHz[citation:1]
#     power=float(audio_params.power)         # 使用功率谱[citation:1]
# )
mel_spectrogram =torchaudio.transforms.MelSpectrogram(
            sample_rate=int(audio_params.sample_rate),
            n_fft=int(audio_params.n_fft),
            hop_length=int(audio_params.hop_length),
            n_mels=int(audio_params.n_mels)
        )

class cope_audio():
    # def __init__(self):
    #     self._T()
    def _mixed_to_mono(self,wav_tensor):
        wav_tensor = wav_tensor.mean(dim=0, keepdim=True)
        wav_tensor = mel_spectrogram(wav_tensor)
        return wav_tensor
    def _the1st_two_channels_to_stereo(self,wav_tensor):
        wav_tensor = wav_tensor[:2, :]  # 前左和前右声道
        wav_tensor = mel_spectrogram(wav_tensor)
        return wav_tensor
    def _cope_each_channels(self,wav_tensor):
        channel_spectrograms = []
        for i in range(wav_tensor.shape[0]):
            channel_spec = mel_spectrogram(wav_tensor[i:i+1, :])
            channel_spectrograms.append(channel_spec)
        wav_tensor=channel_spectrograms
        return wav_tensor
    # def _T(self):
    #     self.transform= torchaudio.transforms.MelSpectrogram(
    #         sample_rate=int(audio_params.sample_rate),
    #         n_fft=int(audio_params.n_fft),
    #         hop_length=int(audio_params.hop_length),
    #         n_mels=int(audio_params.n_mels)
    #     )
    def run(self,wav_tensor:str):
       
        if audio_params.cope_data_mode =="mixed_to_mono":
            # print(">>>   ",wav_tensor.shape)
            wav_tensor = self._mixed_to_mono(wav_tensor)
            # print(">>>   ",wav_tensor.shape)
            # mel_spectrogram = self.transform(wav_tensor)
        elif audio_params.cope_data_mode =="the1st_two_channels_to_stereo":
            wav_tensor =self._the1st_two_channels_to_stereo(wav_tensor)
            # mel_spectrogram = self.transform(wav_tensor)
        elif audio_params.cope_data_mode =="cope_each_channels":
            wav_tensor =self._cope_each_channels(wav_tensor)
            # mel_spectrogram = wav_tensor
        else:
            print("error")
        
        mel_spectrogram = torchaudio.functional.amplitude_to_DB(
                    wav_tensor, multiplier=20, amin=1e-10, db_multiplier=0
                )
        # 确保数值在合理范围内
        mel_spectrogram = torch.clamp(mel_spectrogram, min=0)

        # 转换为3通道图像格式 (为了适配ResNet)
        mel_spectrogram = mel_spectrogram.repeat(3, 1, 1)
        
        # 确保尺寸一致
        resize = torch.nn.AdaptiveAvgPool2d((int(models_params.resize), int(models_params.resize)))
        mel_spectrogram = resize(mel_spectrogram)
        mel_spectrogram =mel_spectrogram.view([1,3,int(models_params.resize), int(models_params.resize)])
        return mel_spectrogram
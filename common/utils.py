import os
import sys
import yaml
import json
import base64
import logging
import jsonlines
from pytz import timezone
from datetime import datetime as dt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from logging.handlers import TimedRotatingFileHandler
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#! 操作文件
def read_jsonl(pth:str,k:int=-5):
    with open(pth, "r", encoding="utf8") as rf:
        data = list(jsonlines.Reader(rf))[k:]
    return data
    
def append_jsonl(pth:str,new_data:list[any]):
    if os.path.exists(pth):
        with jsonlines.open(pth, mode='a') as wf:
            wf.write_all(new_data)
    else:     
        with jsonlines.open(pth, mode='w') as wf:
            wf.write_all(new_data)

def read_json(pth:str)->dict:
    with open(pth,"r",encoding="utf-8") as rf:
        data = json.load(rf)
    return data

def append_json(pth:str,new_data:dict[list]):
    with open(pth,"w",encoding="utf-8") as wf:
        json.dump(new_data,wf,indent=4,ensure_ascii=False)

def read_key(pth):
    tmp_dct = dict()
    with open(pth,'r') as rf:
        lines = rf.readlines()
    for l in lines:
        if l =="" or l.startswith("#"):
            continue
        else:
            k,v = l.split("=")
            k,v = k.strip(),v.strip()
            tmp_dct[k]=v
    return tmp_dct

def read_yaml(path:str)->dict:
    with open(path, 'r', encoding='utf-8') as rf:
        result = yaml.load(rf.read(), Loader=yaml.FullLoader)
    return result

def read_conf(path:str)->dict:
    result = dict()
    # print("path>   " ,path)
    with open(path, 'r', encoding='utf-8') as rf:
        lines = rf.readlines()
        for line in lines:
            line = line.strip()
            b = line.startswith("#")
            if line and (not b):
                name,value = line.split("=")
                name,value = name.strip(),value.strip()
                result[name] = value
    return result


#! 打印
def show_db(n,v=''):
    tm = timepstr(now(),"%m-%d %H:%M:%S")
    print(f"\033[33m[DEBUG]-[{tm}]  {n}  {v}\033[0m")
    
def  show_lg(n,v=''):
    print(f"\033[34m[INFO]  {n}  {v}\033[0m")

def show_er(n,v='',ex=0):
    tm = timepstr(now(),"%m-%d %H:%M:%S")
    print(f"\033[31m[ERROR]-[{tm}]  {n}  {v}\033[0m")
    if ex<0:
        exit(-1)
def show_wn(n, v=''):
    print(f"\033[35m[WARMING]  {n} {v}\033[0m")


# class Logger():
#     def __init__(self): 
#         logger_params = read_conf("configs/logger.conf") 
#         try:
#             logger_params = read_conf("configs/logger.conf")
#         except:
#             logger_params = read_conf("../../../../../configs/logger.conf")
#         self._parse(logger_params)
#         self.log = logging.getLogger()
#         self._set_level()
#         if self.mode in ["local","all"]:
#             self._init_local()
#             self.log.addHandler(self.file_handler)
#         elif self.mode in ["console","all"]:
#             self._init_show()
#             self.log.addHandler(self.console_handler)
#         else:
#             assert ValueError,"mode not local console and all"
        
#     def _parse(self,logger_params):
#         self.name = logger_params["name"]
#         self.level = logger_params["level"]
#         self.out_dir = logger_params["out_dir"]
#         self.when = logger_params["when"]
#         self.backupCount = int(logger_params["backupCount"])
#         self.mode = logger_params["mode"]
#         self.formatter = logging.Formatter(
#             '%(asctime)s - %(levelname)s - %(message)s',  # 时间 | 级别 | 消息
#             datefmt='%Y-%m-%d %H:%M:%S'                 # 时间格式
#         )

#     def _set_level(self):
#         if "debug" == self.level.lower():
#             self.level = logging.DEBUG
#         elif "error" == self.level.lower():
#             self.level = logging.ERROR
#         elif "warning" == self.level.lower():
#             self.level = logging.WARNING
#         else:
#             self.level = logging.INFO
#         # self.log.setLevel(level)
        
#     def _init_local(self):
#         self.file_handler = TimedRotatingFileHandler(
#             filename=os.path.join(self.out_dir,self.name),       # 日志文件名前缀+日期格式
#             when=self.when,                   # 在午夜滚动
#             interval=1,                        # 每隔1天切换
#             backupCount=self.backupCount,                     # 保留最近7天的日志文件
#             encoding='utf-8'                   # 支持中文编码
#         )
#         self.file_handler.setLevel(self.level)
#         self.file_handler.setFormatter(self.formatter)
#     def _init_show(self):
#         self.console_handler = logging.StreamHandler()
#         self.console_handler.setLevel(self.level)
#         self.console_handler.setFormatter(self.formatter)

# class Show():
#     logger = Logger()
#     def debug(self,n, v=''):
#         self.logger.log.debug(f"\033[33m{n} {v}\033[0m")

#     def log(self,n, v=''):
#         self.logger.log.info(f"\033[34m{n} {v}\033[0m")

#     def warm(self,n, v=''):
#         self.logger.log.warning(f"\033[35m{n} {v}\033[0m")

#     def error(self,n, v='', ex=0):
#         self.logger.log.error(f"\033[31m{n} {v}\033[0m")
#         if ex < 0:
#             sys.exit(-1)



#! 时间相关的
def format_date(pubtime_str):
    def get_current_beijing_date():
        tz = timezone('Asia/Shanghai')
        now = dt.now(tz)
        year = now.year
        month = now.month
        day = now.day
        weekday_mapping = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
        weekday = weekday_mapping[now.weekday()]
        return year, month, day, weekday
    time_text = pubtime_str.replace(":", "-")
    year, month, day, weekday = get_current_beijing_date()
    return f"{year}-{month:02}-{day:02}_{weekday}_{time_text}"

def strptime(s:str):
    lst = s.split("_")
    if len(lst) == 3:
        date_str = lst[0] + "_" + lst[-1]
    elif len(lst) == 2:
        date_str = lst[0] + "_" + lst[-1]
    else:
        assert ValueError,"not %Y-%m-%d_%H-%M or %Y-%m-%d_xxx_%H-%M"
    format = "%Y-%m-%d_%H-%M"
    dtdt = dt.strptime(date_str, format)
    return dtdt

def timepstr(dtdt:dt,fmt:str="%m-%d-%y_%H-%M-%S"):
    dt = dtdt.strftime(fmt)
    return dt

def now():
    tm = dt.now()
    return tm

#! 路径相关
def check_file_exist(pth:str):
    if not os.path.exists(pth):
        show_er(f"{pth} not exist")
        
def check_dir(pth:str):
    if not os.path.isdir(pth):
        show_er(f"{pth} not exist")

def mkdir(dir:str):
    os.makedirs(dir,exist_ok=True)


def get_dir(dir:str,file:str)->str:
    tm = dt.now().strftime("%m-%d-%y_%H-%M-%S")
    return os.path.join(dir,tm,file)

def get_latest_directory(pth:str):
    directories = [os.path.join(pth,d) for d in os.listdir(pth) if os.path.isdir(os.path.join(pth,d))]    
    if not directories:
        return None
    latest_directory = max(directories, key=os.path.getctime)    
    return latest_directory




#! 其他
def replace_invalid_chars(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

class dictDotNotation(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self



class EncryptedLatestTracker:
    def __init__(self, user_id:str, password="lanchat_123"):
        self.tracker_file = os.path.join("db_store",user_id,"latest_tracker.enc")
        self.fernet = self._generate_fernet_key(password)
        
    def _generate_fernet_key(self, password):
        """从密码生成加密密钥"""
        password_bytes = password.encode()
        salt = b"fixed_salt_for_consistency"  # 固定盐值，确保每次相同
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return Fernet(key)
    
    def save_latest_tm(self, latest_id):
        """加密保存最新ID"""
        try:
            latest_id = str(latest_id)
            data = latest_id.encode('utf-8')
            encrypted_data = self.fernet.encrypt(data)
            
            with open(self.tracker_file, 'wb') as f:
                f.write(encrypted_data)
                
            return True
        except Exception as e:
            print(f"加密保存最新ID失败: {e}")
            return False
    
    def load_latest_tm(self):
        """解密加载最新ID"""
        try:
            if not os.path.exists(self.tracker_file):
                return None
                
            with open(self.tracker_file, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            print(f"解密加载最新ID失败: {e}")
            return None
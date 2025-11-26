import queue
import pprint
from common.utils import read_conf,dictDotNotation

# load config
run_params = dictDotNotation(read_conf("configs/run.conf"))
audio_params = dictDotNotation(read_conf("configs/wav.conf"))
img_params = dictDotNotation(read_conf("configs/img.conf"))
models_params = dictDotNotation(read_conf("configs/models.conf"))
pprint.pprint(f"load run_params:      {run_params}")
pprint.pprint(f"load audio_params:     {audio_params}")
pprint.pprint(f"load cv2_params    {img_params}")
pprint.pprint(f"load models_params：    {models_params}")

# 
audio_queue = queue.Queue()
img_queue = queue.Queue()
results_queue = queue.Queue()
llm_anasys_results_queue= queue.Queue()
# 
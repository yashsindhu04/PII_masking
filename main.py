import torch
import time
import datetime
from gliner import GLiNER
from ocr import *
from utils import *

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.environ["TESSERACT_PREFER_GPU"] = "1"

# try:
#   model.eval()
# except:
print("Loading model...")
model = GLiNER.from_pretrained("urchade/gliner_multi_pii-v1", cache_dir='pii_model', local_files_only=True, map_location=device)
print("Model loaded")
model.eval()
  
def main(image_path, mode_override=False, is_card=False):
  image = read_image(image_path)
  if is_card:
    chunk_size = 1
  else:
    chunk_size = 5
  chunks, df = extract_text(image, line_size=chunk_size)
  data = batch_flag_pii(chunks, df, check_card=is_card, model=model.to(device))
  redact(image_path, data, mode_override)
  return data

# if __name__ == "__main__":    
# image_path = "samples/pan2.jpg" 
# main(image_path, mode_override=False, is_card=True)
# time_test = pd.DataFrame()
test = pd.DataFrame()
files  = os.listdir('samples')
# times = []
success = []
in_time = []
out_time = []
out_file = []
for file in files:
    if not file.endswith('.csv'):
        start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        in_time.append(start)
        is_card = False if len(file.split('.')[0]) == 1 else True
        try:
          _ = main(os.path.join('samples', file), mode_override=False, is_card=is_card)
          success.append("OK")
        except Exception as e:
          success.append(str(e))          
        end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print(f"{file}: {end-start}s")
        out_time.append(end)
        out_file.append(f"outputs/{file}")
# time_test['filename'] = files
# time_test['time'] = times
test['filename'] = files
test['in_time'] = in_time
test['out_time'] = out_time
test["success"] = success
test["output file"] = out_file
# time_test.to_csv('timed_test_report.csv')
test.to_csv('test.csv')
# filename, success, intime, outtime, out filepath
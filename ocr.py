import pytesseract
import pandas as pd
import numpy as np
import cv2
from PIL import Image
from io import StringIO
import os
import math
from typing import Tuple, Union
from deskew import determine_skew

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSERACT_PREFER_GPU"] = "1"

def rotate(image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]) -> np.ndarray:
  old_width, old_height = image.shape[:2]
  angle_radian = math.radians(angle)
  width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
  height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
  rot_mat[1, 2] += (width - old_width) / 2
  rot_mat[0, 2] += (height - old_height) / 2
  return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)

def read_image(image_path):
  img = Image.open(image_path).convert('L')
  angle = determine_skew(np.array(img))
  img = rotate(np.array(img), angle, (0, 0, 0))
  return img

def extract_text(image, line_size=3):
  data = pytesseract.image_to_data(image, config='--psm 6', lang='eng')
  df = pd.read_csv(StringIO(data), delimiter='\t').dropna(subset=['text'])

  # Clean the text in the DataFrame
  df['text'] = df['text'].str.strip()
  df = df[df['text'] != '']
  df['text'] = df['text'].str.replace(r"[,:;?!*()/.\']", "", regex=True)
  df['text'] = df['text'].str.replace(r'"', '', regex=True)
  df['text'] = df['text'].str.replace(r"'", '', regex=True)
  df.reset_index(inplace=True, drop=True)

  full_text = ""
  current_line_num = -1
  for index, row in df.iterrows():
      if row['line_num'] != current_line_num:
          if current_line_num != -1:
              full_text += "\n"
          current_line_num = row['line_num']
      full_text += row['text'] + " "
  full_text = full_text.strip()

  # Split the full text into chunks based on line_size
  lines = full_text.strip().split('\n')
  chunks = []
  words = lines
  chunks.extend([' '.join(words[i:i+line_size]) for i in range(0, len(words), line_size)])

  return chunks, df
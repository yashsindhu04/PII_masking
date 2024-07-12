import pandas as pd
import numpy as np
import cv2
from PIL import Image
from io import StringIO
import re
import os
import math
from typing import Tuple, Union
from deskew import determine_skew

from ocr import rotate



def batch_flag_pii(chunks, df, model, check_card=False):
  labels = ["person", "phone number", "address",
                "email", "credit card number", "mobile phone number",
                "driver's license number", "identity card number", "national id number",
                "IP address", "email address", "health insurance number", "registration number", "student id number",
                "insurance number", "landline phone number", "cvv", "digital signature",
                "social media handle", "license plate number", "postal code", "passport number",
                "serial number", "vehicle registration number", "national health insurance number",
                "cvc", "birth certificate number"]
  pronouns = ["i", "you", "he", "she", "it",
  "we", "you", "they",
  "my", "mine", "your", "yours", "his", "hers", "its", "our", "ours", "their", "theirs",
  "myself", "yourself", "himself", "herself", "itself", "ourselves", "yourselves", "themselves"]

  temp = df.copy()
  redact_ind = []
  assigned_labels = []
  i = 0
  skip_chunks = np.array([], dtype=int)
  if check_card:
    for skip, text in enumerate(chunks):
      aadhaar_regex = r"\b([2-9][0-9]{3} \s*[0-9]{4} \s*[0-9]{4})\b"
      aadhar_no = re.search(aadhaar_regex, text)

      pan_regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
      pan_no = re.search(pan_regex, text)

      if aadhar_no:
        # print(aadhar_no.group(), "=> aadhar no")
        for s in aadhar_no.group().split()[:-1]:
          df.loc[df.text == s, 'redact'] = True
          df.loc[df.text == s, 'label'] = "aadhaar_no"
          np.append(skip_chunks, skip)

      elif pan_no:
        # print(pan_no.group(), "=> pan no")
        df.loc[df.text == pan_no.group(), 'redact'] = True
        df.loc[df.text == pan_no.group(), 'label'] = "pan_no"
        np.append(skip_chunks, skip)

  chunks = np.array(chunks)
  np.put(chunks, skip_chunks, '')
  chunks = chunks.tolist()

  entities = model.batch_predict_entities(chunks, labels)
  for n in range(len(entities)):
    for entity in entities[n]:
      if entity['score'] >= 0.7:
        # print(entity["text"], "=>", entity["label"], round(entity["score"]*100, 2))
        for word in chunks[n][entity['start']:entity['end']].split():
          # df.loc[df.text.str.replace(f"[{',;:?!*()/'}]", "", regex=True) == word, 'redact'] = True
          # df.loc[df.text == word, 'redact'] = True
          word = word.strip()
          # mask = (temp.text.str.strip(string.punctuation) == word if len(word) > 3 else temp.text == word)
          mask = (temp.text == word)
          # temp.loc[temp.text == word, 'redact'] = True
          temp.loc[mask, 'redact'] = True

          if entity["label"] == "person" and word.lower() in pronouns:
            # temp.loc[temp.text, 'redact'] = False
            temp.loc[mask, 'redact'] = False
            continue
          else:
            assigned_labels.append(entity["label"])
          try:
            ind = temp[mask].index[0]
          except:
            assigned_labels.pop()
            continue
          if i==0:
            redact_ind.append(ind+i)
          else:
            redact_ind.append(ind + (i+1 if ind == 0 else i))
          temp = temp[ind:]
          i += ind
          temp.reset_index(inplace=True, drop=True)

  df.loc[redact_ind, 'redact'] = True
  df.loc[redact_ind, 'label'] = assigned_labels

  return df

def image_masking(image, x, mode_override):
  if mode_override is not False:
    mode = mode_override
  else:
    mode = 'blackout' if x['label'] == 'person' else 'pan' if x['label'] == 'pan_no' else 'XXX'
  if mode == 'blackout':
    cv2.rectangle(image, (x[0], x[1]), (x[0]+x[2], x[1]+x[3]), (0, 0, 0), -1)

  elif mode == 'XXX':
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    font_thickness = 1
    text_color = (0, 0, 0)
    cv2.rectangle(image, (x[0], x[1]), (x[0]+x[2], x[1]+x[3]), (255, 255, 255), -1)
    text = f'X'*len(x['text'])
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    text_x = x[0] + (x[2] - text_size[0]) // 2
    text_y = x[1] + (x[3] + text_size[1]) // 2
    # Ensuring text within bounds
    if text_x < x[0]:
      text_x = x[0]
    if text_y < x[1]:
      text_y = x[1] + x[3]
    cv2.putText(image, text, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

  elif mode == 'pan':
    cv2.rectangle(image, (x[0], x[1]), (x[0]+int(x[2]*0.7), x[1]+x[3]), (0, 0, 0), -1)

def redact(image_path, df, mode_override=False):
  image = cv2.imread(image_path)
  angle = determine_skew(image)
  image = rotate(image, angle, (0, 0, 0))
  df.query('redact == True and conf >= 50')[['left', 'top', 'width', 'height', 'text', 'label']].apply(lambda x: image_masking(image,x, mode_override), axis=1)
  # cv2.imshow("", image)
  # cv2.waitKey(0) 
  # cv2.destroyAllWindows() 
  os.makedirs('outputs', exist_ok=True)
  cv2.imwrite(os.path.join('outputs',image_path.split('\\')[-1]), image)

# **PII Masking for documents and aadhaar/pan cards to redact sensitive information**


## Description

This project automates the masking of Personally Identifiable Information (PII) within images. It combines the power of:

* **Optical Character Recognition (OCR):** Extracts text from images using PyTesseract.
* **DeBERTa:** Identifies PII entities like names, addresses, phone numbers with high accuracy (based on the GLiNER paper by Zaratiana et al., 2023).
* **Regex:** Used to detect Aadhaar numbers and PAN numbers.
* **OpenCV:** Facilitates image processing tasks for masking including separate masking modes.

**Key Features:**

* Comprehensive PII masking, including custom regex for Aadhaar and PAN numbers.
* Fast processing with a benchmark average time of 0.3 seconds per image on an RTX 4060 8GB VRAM.
* Option to mask with different modes like blackout or replace text with asterisks.


**Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   **Note:** Ensure you have Tesseract installed on your system for OCR functionality. You can download it from https://github.com/tesseract-ocr/tesseract.



The DeBERTa model is available locally for use with the code. For details on GLiNER, please refer to the paper:

```
@misc{zaratiana2023gliner,
  title={GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer},
  author={Urchade Zaratiana and Nadi Tomeh and Pierre Holat and Thierry Charnois},
  year={2023},
  eprint={2311.08526},
  archivePrefix={arXiv},
  primaryClass={cs.CL}
}
```
## Contributing

We welcome contributions to this project! Please feel free to submit pull requests that improve functionality, fix bugs, or enhance documentation.

## Authors

Yash Sindhu

Hrithik Konakanchi

For any questions or queries, feel free to reach out: yashsindhu4903@gmail.com

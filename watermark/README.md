# How To Use
## Prerequisite
install blind_watermark
```bash
pip install blind-watermark
```
## add watermark
```bash
python3 watermark.py --add input_directory/ --out output_directory/
```
Copy watermark.py under directory /path/to/directory/, input and output directories are both under /path/to/directory/.
The script will add watermark to images under input_directory/ and its subdirectories, and output to output_directory/.
Meanwhile, a len_wm.txt will be added under input_directory/, which records watermark length of all images.

## add watermark
```bash
python3 watermark.py --extract extract_image --watermark_length watermark_length
```
Copy watermark.py under directory /path/to/directory/, extract image is under /path/to/directory/.
Watermark length is recorded in len_wm.txt.

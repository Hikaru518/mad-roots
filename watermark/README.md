# How To Use
## Prerequisite
Install blind_watermark
```bash
pip install blind-watermark
```
## add watermark
1. Modify watermark.json
2. Under water mark directory
```bash
python3 -m watermark --add input_directory/ --out output_directory/
```
The script will add watermark to images under `input_directory/` and its subdirectories, and output to `output_directory/`.
Meanwhile, a len_wm.txt will be added to `output_directory/`, which records watermark length of all images.

## add watermark
1. Modify watermark.json
2. Under water mark directory
```bash
python3 -m watermark --extract extract_image --watermark_length watermark_length
```
Copy watermark.py under directory `/path/to/directory/`, extract image is under `/path/to/directory/`.
Watermark length is recorded in len_wm.txt.

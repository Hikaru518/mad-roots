import json
from typing import Dict
from pathlib import Path
from PIL import Image, ImageFont
import os


def read_json(file_path: str) -> Dict:
    with open(file_path, "r") as f:
        data = json.load(f)

    return data


class Config(object):
    def __init__(self, config_file_path: str) -> None:
        config_data = read_json(config_file_path)

        # TTS MODE
        self.gen_mode = config_data["GEN_MODE"]

        # input and config
        self.data_dir = Path(config_data["data_dir"]).absolute()
        self.input_csv_filename = config_data["input_csv_filename"]
        self.input_event_csv_filename = config_data["input_event_csv_filename"]
        self.input_csv_filepath = str(self.data_dir / self.input_csv_filename)
        self.input_event_csv_filepath = str(
            self.data_dir / self.input_event_csv_filename
        )
        self.initial_deck_setting = str(
            self.data_dir / config_data["initial_deck_setting"]
        )
        self.cardback_file_path = str(self.data_dir / config_data["cardback_file_name"])

        self.ttf = config_data["ttf"]

        # start settings
        self.start_setting_path = self.data_dir / config_data["start_setting_path"]

        # output
        self.version = config_data["version"]
        self.output_dir = Path(config_data["output_dir"]).absolute()
        self.output_dir_with_version = str(self.output_dir / self.version)

        # font setting
        self.stdfontsize = 30
        font_path = Path(self.data_dir / self.ttf).absolute()
        self.font = ImageFont.truetype(str(font_path), self.stdfontsize)

    @classmethod
    def get_default_config_path(cls):
        current_file_path = Path(os.path.abspath(__file__))
        config_path = current_file_path.parent.parent / "config/config.json"
        return str(config_path)

    def to_dict(self):
        return {
            "TTS_DE_MODE": self.gen_mode,
            "INPUT_CSV_FILE": self.input_csv_filepath,
            "INITIAL_DECK_SETTING": self.initial_deck_setting,
            "OUTPUT_DIR": self.output_dir_with_version,
            "CARDBACK_DIR": self.cardback_file_path,
        }


def PasteImageInTTSFormat(fullImgList, backImg, cols=10, rows=7):
    def PasteBatch(imgList, backImg, cols, rows):
        # 获取图像的宽度和高度
        width, height = imgList[0].size

        # 创建网格图像
        grid = Image.new("RGB", (width * cols, height * rows), color="black")

        # 在网格中粘贴所有图像
        for i in range(min(len(imgList), cols * rows - 1)):
            x = (i % cols) * width
            y = (i // cols) * height
            grid.paste(imgList[i], (x, y))

        # 在最后一个网格中粘贴背景图像
        x = (cols - 1) * width
        y = (rows - 1) * height
        backImg = backImg.resize((width, height))
        grid.paste(backImg, (x, y))

        # 显示或保存图像
        # grid.show()
        # grid.save('output.png')

        return grid

    batchImgList = []
    n = len(fullImgList)
    imgsPerBatch = cols * rows - 1
    batch_number = (n - 1) // imgsPerBatch + 1
    for batch in range(batch_number):
        if batch == batch_number - 1:
            imgList = fullImgList[imgsPerBatch * batch :]
        else:
            imgList = fullImgList[
                imgsPerBatch * batch : imgsPerBatch * batch + imgsPerBatch
            ]
        batchImg = PasteBatch(imgList, backImg, cols, rows)
        batchImgList.append(batchImg)
    return batchImgList

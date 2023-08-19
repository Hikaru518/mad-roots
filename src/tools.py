import json
from typing import Dict
from pathlib import Path
from PIL import Image, ImageFont
import os
from watermark.watermark import WaterMark, get_alldirectories

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

        self.watermark = bool(config_data["watermark"])

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


class WaterMarkProcess(object):
    def __init__(self, config_file_path: str = "") -> None:
        if config_file_path == "":
            current_file_path = Path(os.path.abspath(__file__))
            config_path = current_file_path.parent.parent / "config/watermark.json"
            self.wm = WaterMark(str(config_path))
        else:
            self.wm = WaterMark(config_file_path)

    def add_walk_dir(self, input_dir: str, out_dir: str) -> None:
        input_directory = str(Path(input_dir).absolute())
        output_directory = str(Path(out_dir).absolute())
        all_directories = get_alldirectories(input_directory)
        for directory in all_directories:
            subdirectory = os.path.join(input_directory, directory)
            print("looking into " + subdirectory)
            for file in os.listdir(subdirectory):
                if file.endswith("/"):
                    continue
                self.wm.add_watermark(
                    file,
                    os.path.join(input_directory, directory),
                    os.path.join(output_directory, directory),
                )


    def add_walk_dir_new(self, input_dir: str, out_dir: str) -> None:
        count = 0
        os.makedirs(out_dir, exist_ok=True)
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                # 检查文件扩展名是否为.png
                if file.lower().endswith('.png'):
                    count += 1
                    root_abs = os.path.abspath(root)
                    inputPath = os.path.join(root_abs, file)

                    relativePath = os.path.relpath(inputPath, input_dir)
                    outputPath = os.path.join(out_dir, relativePath)
                    output_dir = str(Path(outputPath).absolute().parent)

                    if not os.path.exists(os.path.dirname(outputPath)):
                        os.makedirs(os.path.dirname(outputPath), exist_ok=True)

                    # print("{0} , {1} => {2}".format(root, file, output_dir))
                    self.wm.add_watermark(file, root_abs, output_dir)

    def add_single_file(self, input_file: str, output_dir: str):

        file_name = str(Path(input_file).absolute().name)
        input_dir = str(Path(input_file).absolute().parent)
        output_dir = str(Path(output_dir).absolute())
        if not Path(input_file).is_file():
            raise Exception("Not a valid file path: {}".format(input_file))

        if not Path(output_dir).is_dir():
            raise Exception("Not a valid dir path: {}".format(output_dir))
        
        self.wm.add_watermark(
            file_name,
            input_dir,
            output_dir,
        )

    def add_wm(self, input_image: Image) -> Image:
        return self.wm.get_water_marked_pil_image(input_image)

    def extract_wm_from_pil_image(self, input_image:Image, wm_length:int) -> str:
        return self.wm.extract_from_pil_image(input_image, wm_length)
    
    def extract_wm_from_file(self, file_name: str, wm_length: int) -> str:
        img = Image.open(file_name)
        return self.wm.extract_from_pil_image(img, wm_length)
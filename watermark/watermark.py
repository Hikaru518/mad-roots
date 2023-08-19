import blind_watermark
import argparse
import os
import json
from typing import Dict
from pathlib import Path
from PIL import Image
import cv2
import numpy

def read_json(file_path: str) -> Dict:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def get_alldirectories(folder: str):
    subdirectories = []
    for root, dirs, _ in os.walk(folder):
        for dir in dirs:
            subdirectories.append(os.path.join(root, dir))
    subdirectories.append(folder)
    all_directories = []
    for subdirectory in subdirectories:
        all_directories.append(subdirectory[len(folder) :])
    all_directories.sort(key=len)
    return all_directories


class WaterMark(object):
    def __init__(self, config_file_path: str = "") -> None:
        if config_file_path == "":
            defaul_config_path = os.path.join(
                os.path.dirname(__file__), "watermark.json"
            )
            config_data = read_json(defaul_config_path)
        else:
            config_data = read_json(config_file_path)

        # input and config
        self._water_mark_text = config_data["water_mark_text"]
        self._password_img = config_data["password_img"]
        self._password_wm = config_data["password_wm"]

        self.bwm = blind_watermark.WaterMark(
            password_img=self._password_img, password_wm=self._password_wm
        )

    def add_watermark(self, file: str, input: str, output: str) -> None:
        input_file = os.path.join(input, file)
        if not os.path.exists(input_file):
            raise Exception(f"input file not found, input path is: {input_file}")

        if not file.endswith(".jpg") and not file.endswith(".png"):
            print(f"skip non image files... current skipped file is: {file}")
            return

        if not os.path.exists(output):
            os.makedirs(output)

        print("adding watermark to " + input_file)
        # read the picture
        self.bwm.read_img(input_file)
        # read the watermark
        watermark = self._water_mark_text
        self.bwm.read_wm(watermark, mode="str")
        # embed the watermark
        output_img = os.path.join(output, f"wm_{file}")
        self.bwm.embed(output_img)
        len_wm = len(self.bwm.wm_bit)

        with open(output + "/len_wm.txt", "a+") as f:
            f.write(file + " " + str(len_wm) + "\n")

        print("put down the length of wm_bit {len_wm}".format(len_wm=len_wm))
        print("watermark added to " + file)

    def extract_watermark(self, file: str, watermark_length: int) -> None:
        if not os.path.exists(file):
            raise Exception(f"extract file not found, path is: {file}")

        if not file.endswith(".jpg") and not file.endswith(".png"):
            print(f"skip non image files... current skipped file is: {file}")

        print("extracting watermark from " + file)

        # read the picture
        wm_extract = self.bwm.extract(file, wm_shape=watermark_length, mode="str")
        print("watermark is ", wm_extract)

    def get_water_marked_pil_image(self, input_image: Image) -> Image:
        # convert PIL image to cv2 image
        numpy_image=numpy.array(input_image)  
        img = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

        self.bwm.read_img(img=img)
        # read the watermark
        watermark = self._water_mark_text
        self.bwm.read_wm(watermark, mode="str")
        # embed the watermark
        embed_image = self.bwm.embed()

        # convert cv2 image to PIL image
        embed_image_mat = cv2.cvtColor(embed_image, cv2.COLOR_BGR2RGB)
        embed_image_mat = embed_image_mat.astype(numpy.uint8)
        res=Image.fromarray(embed_image_mat)

        len_wm = len(self.bwm.wm_bit)
        print(f"length of water mark is: {len_wm}")
        return res

    def extract_from_pil_image(self, input_image: Image, wm_length:int) -> str:
        # convert PIL image to cv2 image
        numpy_image=numpy.array(input_image)  
        img = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

        # extract the watermark
        wm_extract = self.bwm.extract(embed_img=img, wm_shape=wm_length, mode="str")
        return wm_extract


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", "-a", type=str, default="", help="input dir")
    parser.add_argument("--out", "-o", type=str, default="", help="output dir")
    parser.add_argument("--extract", "-e", type=str, default="", help="extract image")
    parser.add_argument(
        "--watermark_length", "-l", type=int, default=0, help="length of watermark"
    )

    args = parser.parse_args()

    current_directory = os.getcwd()
    wm = WaterMark()
    if args.add != "" and args.out != "":
        input_directory = str(Path(args.add).absolute())
        output_directory = str(Path(args.out).absolute())
        all_directories = get_alldirectories(input_directory)
        for directory in all_directories:
            subdirectory = os.path.join(input_directory, directory)
            print("looking into " + subdirectory)
            for file in os.listdir(subdirectory):
                if file.endswith("/"):
                    continue
                wm.add_watermark(
                    file,
                    os.path.join(input_directory, directory),
                    os.path.join(output_directory, directory),
                )
    elif args.extract != "" and args.watermark_length != 0:
        extract_file = str(Path(args.extract).absolute())
        wm.extract_watermark(extract_file, args.watermark_length)
    else:
        print(
            "invalid arguments, input add dir + out dir or extract image + watermark length"
        )

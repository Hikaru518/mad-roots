from src.tools import WaterMarkProcess
from PIL import Image
import os

def test_write_file():
    wmp = WaterMarkProcess()
    wmp.add_single_file("./test/test.png", "./test/wm_added.png")


def test_get_PIL_image(wm_length:int):
    wmp = WaterMarkProcess()
    img = Image.open("./test/card_103_2.png")
    embed = wmp.add_wm(img) 
    embed.save("embed.png")

    extract_from_img = wmp.extract_wm_from_pil_image(embed, wm_length)
    print("extract wm from pil image: ", extract_from_img)

    extract_from_file = wmp.extract_wm_from_file("embed.png", wm_length)
    print("extract wm from file, water mark is: ", extract_from_file)

def test_extract(filename, wm_length:int):
    wmp = WaterMarkProcess()
    watermarked_img = Image.open(filename)
    extracted_string = wmp.extract_wm_from_pil_image(watermarked_img, wm_length)
    print(filename + " => " + extracted_string)

def test_walk(originFolder, wmFolder):
    wmp = WaterMarkProcess()
    print("Add watermark in folder: " + os.path.abspath(originFolder) + " => " + os.path.abspath(wmFolder))
    wmp.add_walk_dir(originFolder, wmFolder)


if __name__ == "__main__":
    test_extract("sample.png")

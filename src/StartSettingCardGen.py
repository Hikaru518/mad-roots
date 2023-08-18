from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
import textwrap
import csv
import os
from shutil import copyfile
import json
from src.tools import read_json
from pathlib import Path
from pprint import pprint

from CardGenV2 import Config, PasteImageInTTSFormat




class StartInfo:
    def __init__(self, ID, size, fertileList, poisonousList, stoneList):
        self.ID = ID
        self.size = size
        self.fertileList = fertileList
        self.poisonousList = poisonousList
        self.stoneList = stoneList


def LocateByIndex(size, index, cellsize, offset = (0,0)):
    cols = size[1]
    i = index % cols
    j = index // cols
    result_x = offset[0] + cellsize[0] * i
    result_y = offset[1] + cellsize[1] * j
    return int(result_x), int(result_y)


def GenStartSettingCard(info: StartInfo, config: Config):
    boardImgOffset = (70, 275)
    tileOffset = (180, 386)
    tileImgSize = (80, 80)
    tileGapSize = (87.5, 87.5)

    startSettingDataFolder = config.start_setting_path
    img = Image.open(startSettingDataFolder / "cardTemplate.png")

    boardImg = Image.open(startSettingDataFolder / "board.png")
    boardImg = boardImg.resize([651, 651])
    img.paste(boardImg, boardImgOffset)


    fertileImg = Image.open(startSettingDataFolder / "fertile.png")
    fertileImg = fertileImg.resize(tileImgSize)
    for fertileIndex in info.fertileList:
        img.paste(fertileImg, LocateByIndex(info.size, fertileIndex, tileGapSize, tileOffset))

    poisonousImg = Image.open(startSettingDataFolder / "poisonous.png")
    poisonousImg = poisonousImg.resize(tileImgSize)
    for poisonousIndex in info.poisonousList:
        img.paste(poisonousImg, LocateByIndex(info.size, poisonousIndex, tileGapSize, tileOffset))

    stoneImg = Image.open(startSettingDataFolder / "stone.png")
    stoneImg = stoneImg.resize(tileImgSize)
    for stoneIndex in info.stoneList:
        img.paste(stoneImg, LocateByIndex(info.size, stoneIndex, tileGapSize, tileOffset))

    #img.save(startSettingDataFolder / "cardTest1.png")
    return img


def GenStartSettingCardBatch(config: Config):
    #print(config.start_setting_path)
    dataPath = Path(config.start_setting_path) / "startData.csv"
    genImgList = []
    with open(dataPath, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            ID = row[0]
            print(row)
            ferList = list(int(x) for x in str(row[1]).replace('"',"").split(","))
            poisonList = list(int(x) for x in str(row[2]).replace('"', "").split(","))
            stoneList = list(int(x) for x in str(row[3]).replace('"', "").split(","))
            startInfo = StartInfo(ID, (5,5), ferList, poisonList, stoneList)
            genImg = GenStartSettingCard(startInfo, config)
            genImgList.append(genImg)
    return genImgList

def gen_start_setting_card_raw(config: Config):
    genImgList = GenStartSettingCardBatch(config)
    outputDir = config.output_dir_with_version/ Path("startSettingRaw")
    os.makedirs(outputDir, exist_ok=True)
    count = 0
    for genImg in genImgList:
        count += 1
        imgForceShaped = genImg.resize((684, 1044))
        imgForceShaped.save(os.path.join(outputDir, "startSetting_{0}.png".format(count)))

def gen_start_setting_card_atlas(config: Config):
    genImgList = GenStartSettingCard(Config)
    backImg = Image.open(config.start_setting_path / "cardTemplate.png")
    atlasImg = PasteImageInTTSFormat(genImgList, backImg, cols=5, rows=4)
    output_dir = config.output_dir_with_version / Path("atlas") / Path("startSettingCard.png")
    atlasImg[0].save(output_dir)

if __name__ == "__main__":
    # startInfoTest = StartInfo(0, (5, 5), [0, 2, 8, 20, 24], [3, 16, 19], [23])
    # GenStartSettingCard(startInfoTest, config)


    default_config_path = Config.get_default_config_path()
    config = Config(default_config_path)

    # gen_start_setting_card_atlas(config)
    gen_start_setting_card_raw(config)

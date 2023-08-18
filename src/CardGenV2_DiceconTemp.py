from PIL import Image, ImageDraw, ImageFont
import textwrap
import csv
import os
from shutil import copyfile
from pathlib import Path
from pprint import pprint
from src.tools import Config, PasteImageInTTSFormat
from src.ColorMap import COLOR_MAP, COLOR_MAP_CMYK
from enum import Enum
from typing import List
from CMYK_Converter import rgb_to_cmyk, normalize_cmyk

############################################
# GEN_MODE:
# ttsde: 按照TTS Deck Builder的格式生成文件 每张卡只生成一张图片 例如有3张 105卡牌，则生成文件名是"03x card_105.png"
#       TTS_DE_MODE 会在OUTPUT_DIR目录下自动生成三个文件夹：initialDeck, market和onBoard，分别对应了玩家初始套牌，市场牌和常驻牌（如向日葵和圣甲虫）
#       这样的好处是导入进TTS之后会自动按照功能一摞一摞分好，不用再进行整理了。
# tts: *推荐* 直接生成可以批量导入tts的图集，是若干张10*7的atlas大图，每张最多包含69张卡牌图片和1张卡背图片。
# raw: 每一张卡牌生成一张图片，有3张105卡牌就会生成3个一样的文件 名为 "card_105_X.png"

# INPUT_CSV_FILE: 一个csv文件，记录了所有卡牌信息，可以直接从V0.6规则中的“导出视图”复制粘贴过来
# OUTPUT_DIR: 输出路径，最好是一个空文件夹
# INITIAL_DECK_SETTING: 一个txt文件，记录了玩家初始套牌有哪些卡，格式如："101:6,102:4,103:2"
# CARDBACK_DIR: 牌背png图像


# 注意：
# 卡牌插图会固定读取路径为"Images/CardIcon/XXX.png"的图片，其中XXX为卡牌数字ID。
# 卡牌底板在"Images/CardTemplate"文件夹中，会读取卡牌的派系名称，并在此文件夹中找到对应图片作为底板，可以替换这些图片文件但不要改名。


# (125,139,152)
standardWhiteColor = COLOR_MAP_CMYK["standardWhiteColor"]
standardBlackColor = COLOR_MAP_CMYK["standardBlackColor"]


class GenModeEnum(Enum):
    TTS_DECK_EDITOR = "ttsde"
    TTS = "tts"
    RAW = "raw"


class ImageInfo:
    def __init__(
        self, cardType, cardClass, sunCost, coinCost, name, desciption, cardID, repeat_count
    ):
        self.cardType = cardType
        self.cardClass = cardClass
        self.sunCost = sunCost
        self.coinCost = coinCost
        self.name = name
        self.description = desciption
        self.cardID = cardID
        self.repeat_count = repeat_count

    @classmethod
    def has_cardClass(cls, cardClass: str):
        if cardClass in ["化学", "机械", "巫术", "自然", "神秘", "怪物", "常驻"]:
            return True
        return False

    def classText(self):
        if self.cardClass == "常驻":
            return self.cardClass + " - " + self.cardType
        elif self.cardType == "怪物":
            return "怪物"
        else:
            return self.cardClass + " - " + self.cardType


def GenImage(info: ImageInfo, outputDir: str, config: Config):
    font = config.font

    def DrawText(text, fontsize, xy, colorCMYK, anchor):
        usingFont = font.font_variant(size=fontsize)
        colorCMYK = normalize_cmyk(colorCMYK, 100, 255)
        #print(colorCMYK)
        draw.text(xy, text, fill=colorCMYK, font=usingFont, anchor=anchor)

    def DrawMultilineText(text, fontsize, xy, colorCMYK, anchor):
        lines = textwrap.wrap(text, width=12)
        y_text = xy[1]
        for line in lines:
            # print(line)
            bbox = font.getbbox(line)
            height = fontsize
            DrawText(line, fontsize, (xy[0], y_text), colorCMYK, anchor)
            y_text += height * 1.3

    templateCode = info.cardClass
    if not ImageInfo.has_cardClass(info.cardClass):
        templateCode = "常驻"
    if info.cardClass == "常驻" and info.cardType == "怪物":
        templateCode = "怪物"
    classTextColor = COLOR_MAP_CMYK[templateCode]["classTextColor"]
    descriptionColor = COLOR_MAP_CMYK[templateCode]["descriptionColor"]
    cardNameColor = standardWhiteColor

    #templateCode = "自然"

    cardTemplateFolder = Path(config.data_dir) / "DiceconTemplate"
    # bottomLayerDir = cardTemplateFolder / "Template" / "BottomLayer.png"
    # templateDirL1 = cardTemplateFolder / "Template" / f"{templateCode}_Bg.png"
    # if templateCode == "怪物":
    #     templateDirL2 = cardTemplateFolder / "Template" / f"{templateCode}.png"
    # else:
    #     if info.cardType == "设备":
    #         templateDirL2 = cardTemplateFolder / "Template" / f"{templateCode}_Facility.png"
    #     else:
    #         templateDirL2 = cardTemplateFolder / "Template" / f"{templateCode}_Action.png"

    templateDirR1 = cardTemplateFolder / "Cards" / f"card_{info.cardID}_1.tif"
    templateDirR2 = cardTemplateFolder / "Cards" / f"card_{info.cardID}_1.tiff"

    if os.path.exists(templateDirR1):
        templateDirBackground = templateDirR1
    elif os.path.exists(templateDirR2):
        templateDirBackground = templateDirR2
    else:
        return

    # template L1 底板
    img = Image.open(templateDirBackground)
    img = img.resize((697, 1087))
    #img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # classIcon
    classIconDir = cardTemplateFolder / "Icon" / f"{templateCode}.png"
    classIcon = Image.open(classIconDir)
    cmx, cmy = classIcon.size
    img.paste(classIcon, (66 - cmx // 2, 67 - cmy // 2), mask=classIcon)

    # classText
    #print("classtextcolor")
    DrawText(info.classText(), 38, (103, 48), classTextColor, "lt")

    if int(info.sunCost) > 0:  # sunCost
        costIconDir = cardTemplateFolder / "Icon" / "阳光.png"
        costIcon = Image.open(costIconDir)
        cmx, cmy = costIcon.size
        img.paste(costIcon, (525, 36), mask=costIcon)
        #print("standardBlackColor")
        DrawText(info.sunCost, 55, (590, 99), standardBlackColor, "mm")
    else:  # coinCost
        costIconDir = cardTemplateFolder / "Icon" / "银币.png"
        costIcon = Image.open(costIconDir)
        cmx, cmy = costIcon.size
        img.paste(costIcon, (537, 41), mask=costIcon)
        #print("standardBlackColor")
        DrawText(info.coinCost, 55, (590, 99), standardBlackColor, "mm")

    # name
    #print("cardNameColor")
    DrawText(info.name, 60, (348, 602), cardNameColor, "mm")

    # discription
    #print("descriptionColor")
    DrawMultilineText(info.description, 42, (95, 723), descriptionColor, "lm")

    # 保存图片
    if outputDir:
        imgForceShaped = img.resize((684, 1044))
        img = img.convert("CMYK")
        imgForceShaped.save(outputDir)
    return img

class ImageConverter(object):
    def __init__(self, config_path: str) -> None:
        self.config = Config(config_path)

        self.GEN_MODE = self.config.gen_mode
        self.INPUT_CSV_FILE = self.config.input_csv_filepath  # input csv file
        self.INITIAL_DECK_SETTING = self.config.initial_deck_setting
        self.OUTPUT_DIR = self.config.output_dir_with_version
        self.CARDBACK_DIR = self.config.cardback_file_path
        pass

    def run(self):
        initialDeckDict = self.__get_deck_dict()
        image_info_list = self.__get_image_info_list()

        if self.GEN_MODE == GenModeEnum.TTS_DECK_EDITOR.value:
            self.generate_tts_deck_editor(image_info_list, initialDeckDict)
        elif self.GEN_MODE == GenModeEnum.TTS.value:
            self.generate_tts(image_info_list, initialDeckDict)
        elif self.GEN_MODE == GenModeEnum.RAW.value:
            self.generate_raw_card(image_info_list, initialDeckDict)
        else:
            print(f"GEN_MODE = {self.GEN_MODE}")
            raise Exception("Error: GEN_MODE must be one of ttsde/tts/raw")

    def generate_tts_deck_editor(
        self, image_info_list: List[ImageInfo], initialDeckDict: dict
    ):
        # create output dir
        if not os.path.exists(self.OUTPUT_DIR):
            os.mkdir(self.OUTPUT_DIR)

        # init output dir
        if not os.path.exists(os.path.join(self.OUTPUT_DIR, "market")):
            os.mkdir(os.path.join(self.OUTPUT_DIR, "market"))
        if not os.path.exists(os.path.join(self.OUTPUT_DIR, "onBoard")):
            os.mkdir(os.path.join(self.OUTPUT_DIR, "onBoard"))
        if not os.path.exists(os.path.join(self.OUTPUT_DIR, "initialDeck")):
            os.mkdir(os.path.join(self.OUTPUT_DIR, "initialDeck"))

        # generate card
        for image_info in image_info_list:
            output_dir_root = self.OUTPUT_DIR
            file_name = "{0:0>2}x card_{1}.png".format(
                image_info.repeat_count, image_info.cardID
            )
            if image_info.cardClass == "常驻":
                outputDir = os.path.join(output_dir_root, "onBoard", file_name)
            else:
                outputDir = os.path.join(output_dir_root, "market", file_name)

            GenImage(image_info, outputDir, self.config)

            # 生成初始卡组
            if image_info.cardID in initialDeckDict.keys():
                outputDir = os.path.join(
                    self.OUTPUT_DIR,
                    "initialDeck",
                    "{0:0>2}x card_{1}.png".format(
                        initialDeckDict[image_info.cardID], image_info.cardID
                    ),
                )
                GenImage(image_info, outputDir, self.config)

        copyfile(
            self.CARDBACK_DIR, os.path.join(self.OUTPUT_DIR, "market", "00 Back.png")
        )
        copyfile(
            self.CARDBACK_DIR, os.path.join(self.OUTPUT_DIR, "onBoard", "00 Back.png")
        )
        copyfile(
            self.CARDBACK_DIR,
            os.path.join(self.OUTPUT_DIR, "initialDeck", "00 Back.png"),
        )

    def generate_tts(self, image_info_list: List[ImageInfo], initialDeckDict: dict):
        imgListMarket = []
        imgListOnBoard = []
        imgListInitial = []

        # create output dir
        if not os.path.exists(self.OUTPUT_DIR):
            os.mkdir(self.OUTPUT_DIR)

        if not os.path.exists(os.path.join(self.OUTPUT_DIR, "atlas")):
            os.mkdir(os.path.join(self.OUTPUT_DIR, "atlas"))

        for image_info in image_info_list:
            image = GenImage(image_info, "", self.config)
            if image_info.cardClass == "常驻":
                for _ in range(image_info.repeat_count):
                    imgListOnBoard.append(image)
            else:
                for _ in range(image_info.repeat_count):
                    imgListMarket.append(image)

            # 生成初始卡组
            if image_info.cardID in initialDeckDict.keys():
                for _ in range(initialDeckDict[image_info.cardID]):
                    imgListInitial.append(image)

        print("正在拼接大图，请稍等....")
        backImg = Image.open(self.CARDBACK_DIR)
        batchimgListMarket = PasteImageInTTSFormat(imgListMarket, backImg, 10, 7)
        batchimgListOnBoard = PasteImageInTTSFormat(imgListOnBoard, backImg, 10, 7)
        batchimgListInitial = PasteImageInTTSFormat(imgListInitial, backImg, 10, 7)
        for i in range(len(batchimgListMarket)):
            outputDir = os.path.join(
                self.OUTPUT_DIR, "atlas", "market_{0}.png".format(i + 1)
            )
            batchimgListMarket[i].save(outputDir)
        print("1/3")
        for i in range(len(batchimgListOnBoard)):
            outputDir = os.path.join(
                self.OUTPUT_DIR, "atlas", "onBoard_{0}.png".format(i + 1)
            )
            batchimgListOnBoard[i].save(outputDir)
        print("2/3")
        for i in range(len(batchimgListInitial)):
            outputDir = os.path.join(
                self.OUTPUT_DIR, "atlas", "initialDeck_{0}.png".format(i + 1)
            )
            batchimgListInitial[i].save(outputDir)
        print("3/3")
        print("拼接完成")

    def generate_raw_card(self, image_info_list: List[ImageInfo], initialDeckDict: dict, playerCount = 3):
        if not os.path.exists(self.OUTPUT_DIR):
            os.mkdir(self.OUTPUT_DIR)

        if not os.path.exists(os.path.join(self.OUTPUT_DIR, "cardRaw")):
            os.mkdir(os.path.join(self.OUTPUT_DIR, "cardRaw"))

        for image_info in image_info_list:
            for i in range(image_info.repeat_count):
                outputDir = os.path.join(
                    self.OUTPUT_DIR,
                    "cardRaw",
                    "card_{0}_{1}.tiff".format(image_info.cardID, i + 1),
                )
                GenImage(image_info, outputDir, self.config)

            if image_info.cardID in initialDeckDict.keys():
                for i in range(playerCount * initialDeckDict[image_info.cardID]):
                    initialCardOutputDir = os.path.join(
                        self.OUTPUT_DIR,
                        "cardRaw",
                        "cardInitial_{0}_{1}.tiff".format(image_info.cardID, i + 1),
                    )
                    GenImage(image_info, initialCardOutputDir, self.config)

    def __get_deck_dict(self) -> dict:
        config = self.config
        print("config is: ")
        pprint(config.to_dict())

        # 参数
        initialDeckDict = dict()
        with open(
            self.INITIAL_DECK_SETTING, newline="", encoding="utf-8"
        ) as initialSettingFile:
            initialString = initialSettingFile.readline()
            cardList = initialString.split(",")
            for pairString in cardList:
                pair = pairString.split(":")
                initialCardId = int(pair[0])
                initialCardNumber = int(pair[1])
                initialDeckDict[initialCardId] = initialCardNumber
        print("初始套牌：" + str(initialDeckDict))
        return initialDeckDict

    def __get_image_info_list(self) -> List[ImageInfo]:
        result = list()  # type: List[ImageInfo]
        with open(self.INPUT_CSV_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过第一行，即标题行
            completed = 0
            for row in reader:
                # 处理每一行数据 type, classText, sunCost, coinCost, name, desciption, cardID
                print("{0} {1}".format(completed, row))
                cardType = row[1]
                cardClass = row[2]
                sunCost = row[4]
                coinCost = row[3]
                name = row[0]
                description = row[5]
                repeatCount = int(row[6])
                cardID = int(row[7])
                imageInfo = ImageInfo(
                    cardType,
                    cardClass,
                    sunCost,
                    coinCost,
                    name,
                    description,
                    cardID,
                    repeatCount,
                )
                result.append(imageInfo)
                completed += 1

        return result


if __name__ == "__main__":
    # default config path
    default_config_path = Config.get_default_config_path()

    image_converter = ImageConverter(config_path=default_config_path)
    image_converter.run()




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
standardWhiteColor = (251, 240, 217)
standardBlackColor = (65, 65, 65)


class Config(object):
    def __init__(self, config_file_path: str) -> None:
        config_data = read_json(config_file_path)

        # TTS MODE
        self.tts_mode = config_data["GEN_MODE"]

        # input and config
        self.data_dir = Path(config_data["data_dir"]).absolute()
        self.input_csv_filename = config_data["input_csv_filename"]
        self.input_csv_filepath = str(self.data_dir / self.input_csv_filename)
        self.initial_deck_setting = str(
            self.data_dir / config_data["initial_deck_setting"]
        )
        self.cardback_file_path = str(self.data_dir / config_data["cardback_file_name"])

        self.ttf = config_data["ttf"]

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
            "TTS_DE_MODE": self.tts_mode,
            "INPUT_CSV_FILE": self.input_csv_filepath,
            "INITIAL_DECK_SETTING": self.initial_deck_setting,
            "OUTPUT_DIR": self.output_dir_with_version,
            "CARDBACK_DIR": self.cardback_file_path,
        }


class ImageInfo:
    def __init__(self, type, classText, sunCost, coinCost, name, desciption, cardID):
        self.type = type
        self.classText = classText
        self.sunCost = sunCost
        self.coinCost = coinCost
        self.name = name
        self.description = desciption
        self.cardID = cardID


def GenImage(info: ImageInfo, outputDir: str, config: Config):
    font = config.font

    def DrawText(text, fontsize, xy, colorRGB, anchor):
        usingFont = font.font_variant(size=fontsize)
        draw.text(xy, text, fill=colorRGB, font=usingFont, anchor=anchor)

    def DrawMultilineText(text, fontsize, xy, colorRGB, anchor):
        lines = textwrap.wrap(text, width=12)
        y_text = xy[1]
        for line in lines:
            # print(line)
            bbox = font.getbbox(line)
            height = fontsize
            DrawText(line, fontsize, (xy[0], y_text), colorRGB, anchor)
            y_text += height * 1.25

    if info.type == "化学":
        templateDir = "化学.png"
        classTextColor = (29, 48, 161)
        descriptionColor = (125, 139, 151)
        cardNameColor = standardWhiteColor
    elif info.type == "机械":
        templateDir = "机械.png"
        classTextColor = (103, 64, 29)
        descriptionColor = (153, 138, 111)
        cardNameColor = standardWhiteColor
    elif info.type == "巫术":
        templateDir = "巫术.png"
        classTextColor = (78, 19, 102)
        descriptionColor = (124, 104, 125)
        cardNameColor = standardWhiteColor
    elif info.type == "自然":
        templateDir = "自然.png"
        classTextColor = (28, 75, 24)
        descriptionColor = (80, 106, 54)
        cardNameColor = standardWhiteColor
    elif info.type == "神秘":
        templateDir = "神秘.png"
        classTextColor = (54, 54, 54)
        descriptionColor = (118, 123, 129)
        cardNameColor = standardBlackColor
    else:
        templateDir = "通用.png"
        classTextColor = (90, 90, 90)
        descriptionColor = (128, 139, 151)
        cardNameColor = standardWhiteColor
    card_template = Path(config.data_dir) / "CardTemplate"
    templateFullDir = str(card_template / templateDir)

    img = Image.open(templateFullDir)
    draw = ImageDraw.Draw(img)

    # classText
    DrawText(info.classText, 64, (64, 75), classTextColor, "lt")

    # coinCost
    DrawText(info.coinCost, 56, (551, 102), standardWhiteColor, "lt")

    # sunCost
    DrawText(info.sunCost, 56, (660, 95), standardWhiteColor, "lt")

    # name
    DrawText(info.name, 72, (395, 719), cardNameColor, "mm")

    # discription
    DrawMultilineText(info.description, 48, (100, 864), descriptionColor, "lm")

    fullIconDir = str(config.data_dir / f"CardIcon/{info.cardID}.png")
    if os.path.exists(fullIconDir):
        cardIcon = Image.open(fullIconDir)
        cmx, cmy = cardIcon.size
        img.paste(cardIcon, (396 - cmx // 2, 430 - cmy // 2), mask=cardIcon)
    else:
        pass
        # cardIcon = Image.open("Images/CardIcon/fallback.png")
        # cmx, cmy = cardIcon.size
        # img.paste(cardIcon, (396 - cmx // 2, 430 - cmy // 2), mask=cardIcon)

    # 保存图片
    if outputDir:
        img.save(outputDir)
    return img

def PasteImageInTTSFormat(fullImgList, backImg):
    def PasteBatch(imgList, backImg):
        # 获取图像的宽度和高度
        width, height = imgList[0].size

        # 创建网格图像
        grid = Image.new('RGB', (width * 10, height * 7), color='black')

        # 在网格中粘贴所有图像
        for i in range(min(len(imgList), 69)):
            x = (i % 10) * width
            y = (i // 10) * height
            grid.paste(imgList[i], (x, y))

        # 在最后一个网格中粘贴背景图像
        x = 9 * width
        y = 6 * height
        grid.paste(backImg, (x, y))

        # 显示或保存图像
        #grid.show()
        #grid.save('output.png')

        return grid

    batchImgList = []
    n = len(fullImgList)
    batch_number = (n - 1) // 69 + 1
    for batch in range(batch_number):
        if batch == batch_number - 1:
            imgList = fullImgList[69 * batch:]
        else:
            imgList = fullImgList[69 * batch: 69 * batch + 69]
        batchImg = PasteBatch(imgList, backImg)
        batchImgList.append(batchImg)
    return batchImgList




def convert_to_images(config_file: str):
    config = Config(config_file)
    pprint(config.to_dict())

    # 参数
    GEN_MODE = config.tts_mode
    INPUT_CSV_FILE = config.input_csv_filepath  # input csv file
    INITIAL_DECK_SETTING = config.initial_deck_setting
    OUTPUT_DIR = config.output_dir_with_version
    CARDBACK_DIR = config.cardback_file_path

    initialDeckDict = dict()
    with open(INITIAL_DECK_SETTING, newline="", encoding="utf-8") as initialSettingFile:
        initialString = initialSettingFile.readline()
        cardList = initialString.split(",")
        for pairString in cardList:
            pair = pairString.split(":")
            initialCardId = int(pair[0])
            initialCardNumber = int(pair[1])
            initialDeckDict[initialCardId] = initialCardNumber
    print("初始套牌：" + str(initialDeckDict))

    with open(INPUT_CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过第一行，即标题行
        completed = 0

        if not os.path.exists(OUTPUT_DIR):
            Path(OUTPUT_DIR).mkdir()

        if GEN_MODE == "ttsde":
            if not os.path.exists(os.path.join(OUTPUT_DIR, "market")):
                os.mkdir(os.path.join(OUTPUT_DIR, "market"))
            if not os.path.exists(os.path.join(OUTPUT_DIR, "onBoard")):
                os.mkdir(os.path.join(OUTPUT_DIR, "onBoard"))
            if not os.path.exists(os.path.join(OUTPUT_DIR, "initialDeck")):
                os.mkdir(os.path.join(OUTPUT_DIR, "initialDeck"))

        if GEN_MODE == "tts":
            imgListMarket = []
            imgListOnBoard = []
            imgListInitial = []
            if not os.path.exists(os.path.join(OUTPUT_DIR, "atlas")):
                os.mkdir(os.path.join(OUTPUT_DIR, "atlas"))

        for row in reader:
            # 处理每一行数据 type, classText, sunCost, coinCost, name, desciption, cardID
            print("{0} {1}".format(completed, row))
            type = row[2]
            classText = row[2] + " - " + row[1]
            sunCost = row[4]
            coinCost = row[3]
            name = row[0]
            description = row[5]
            repeatCount = int(row[6])
            cardID = int(row[7])
            imageInfo = ImageInfo(
                type, classText, sunCost, coinCost, name, description, cardID
            )
            # ttsde模式: 生成单独的图像 名称为 "03x card_123.png"，用于在tts deck editor中处理
            if GEN_MODE == "ttsde":
                if row[2] == "常驻":
                    outputDir = os.path.join(
                        OUTPUT_DIR,
                        "onBoard",
                        "{0:0>2}x card_{1}.png".format(repeatCount, cardID),
                    )
                    GenImage(imageInfo, outputDir, config)
                else:
                    outputDir = os.path.join(
                        OUTPUT_DIR,
                        "market",
                        "{0:0>2}x card_{1}.png".format(repeatCount, cardID),
                    )
                    GenImage(imageInfo, outputDir, config)

                # 生成初始卡组
                if cardID in initialDeckDict.keys():
                    outputDir = os.path.join(
                        OUTPUT_DIR,
                        "initialDeck",
                        "{0:0>2}x card_{1}.png".format(initialDeckDict[cardID], cardID),
                    )
                    GenImage(imageInfo, outputDir, config)

            # tts模式：直接生成少数几张模板，每张模板为10x7，最后一张是牌背的tts导入格式。
            elif GEN_MODE == "tts":
                if row[2] == "常驻":

                    image = GenImage(imageInfo, "", config)
                    for _ in range(repeatCount):
                        imgListOnBoard.append(image)
                else:
                    outputDir = os.path.join(
                        OUTPUT_DIR,
                        "market",
                        "{0:0>2}x card_{1}.png".format(repeatCount, cardID),
                    )
                    image = GenImage(imageInfo, "", config)
                    for _ in range(repeatCount):
                        imgListMarket.append(image)

                # 生成初始卡组
                if cardID in initialDeckDict.keys():
                    outputDir = os.path.join(
                        OUTPUT_DIR,
                        "initialDeck",
                        "{0:0>2}x card_{1}.png".format(initialDeckDict[cardID], cardID),
                    )
                    image = GenImage(imageInfo, "", config)
                    for _ in range(repeatCount):
                        imgListInitial.append(image)

            # raw模式：生成若干图像，每张图像对应现实中的一张卡，方便打印（或许）
            else:
                for i in range(repeatCount):
                    outputDir = os.path.join(
                        OUTPUT_DIR, "card_{0}_{1}.png".format(cardID, i + 1)
                    )
                    GenImage(imageInfo, outputDir, config)
            completed += 1


        # 后处理

        # 卡背 png 图像
        if GEN_MODE == "ttsde":
            copyfile(CARDBACK_DIR, os.path.join(OUTPUT_DIR, "market", "00 Back.png"))
            copyfile(CARDBACK_DIR, os.path.join(OUTPUT_DIR, "onBoard", "00 Back.png"))
            copyfile(
                CARDBACK_DIR, os.path.join(OUTPUT_DIR, "initialDeck", "00 Back.png")
            )
        # 拼接atlas大图并保存
        elif GEN_MODE == "tts":
            print("正在拼接大图，请稍等....")
            backImg = Image.open(CARDBACK_DIR)
            batchimgListMarket = PasteImageInTTSFormat(imgListMarket, backImg)
            batchimgListOnBoard = PasteImageInTTSFormat(imgListOnBoard, backImg)
            batchimgListInitial = PasteImageInTTSFormat(imgListInitial, backImg)
            for i in range(len(batchimgListMarket)):
                outputDir = os.path.join(OUTPUT_DIR, "atlas", "market_{0}.png".format(i + 1))
                batchimgListMarket[i].save(outputDir)
            print("1/3")
            for i in range(len(batchimgListOnBoard)):
                outputDir = os.path.join(OUTPUT_DIR, "atlas", "onBoard_{0}.png".format(i + 1))
                batchimgListOnBoard[i].save(outputDir)
            print("2/3")
            for i in range(len(batchimgListInitial)):
                outputDir = os.path.join(OUTPUT_DIR, "atlas", "initialDeck_{0}.png".format(i + 1))
                batchimgListInitial[i].save(outputDir)
            print("3/3")
            print("拼接完成")


if __name__ == "__main__":
    # default config path
    default_config_path = Config.get_default_config_path()

    convert_to_images(default_config_path)

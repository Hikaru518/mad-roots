from PIL import Image, ImageDraw, ImageFont
import textwrap
import csv
import os
from shutil import copyfile

stdfontsize = 30
font = ImageFont.truetype("../data/Chusung.ttf", stdfontsize)


class ImageInfo:
    def __init__(self, type, classText, sunCost, coinCost, name, desciption, cardID):
        self.type = type
        self.classText = classText
        self.sunCost = sunCost
        self.coinCost = coinCost
        self.name = name
        self.description = desciption
        self.cardID = cardID


# (125,139,152)
standardWhiteColor = (251, 240, 217)
standardBlackColor = (65, 65, 65)


def GenImage(info: ImageInfo, outputDir: str):
    def DrawText(text, fontsize, xy, colorRGB, anchor):
        font = ImageFont.truetype("../data/Chusung.ttf", fontsize)
        draw.text(xy, text, fill=colorRGB, font=font, anchor=anchor)

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
    templateFullDir = os.path.join("../data/CardTemplate", templateDir)

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

    fullIconDir = "../data/CardIcon/{0}.png".format(info.cardID)
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
    img.save(outputDir)


############################################
# 在这里改参数！
# TTS_DE_MODE:
# True: 按照TTS Deck Builder的格式生成文件 每张卡只生成一张图片 例如有3张 105卡牌，则生成文件名是"03x card_105.png"
#       TTS_DE_MODE 会在OUTPUT_DIR目录下自动生成三个文件夹：initialDeck, market和onBoard，分别对应了玩家初始套牌，市场牌和常驻牌（如向日葵和圣甲虫）
#       这样的好处是导入进TTS之后会自动按照功能一摞一摞分好，不用再进行整理了。
# False: 每一张卡牌生成一张图片，有3张105卡牌就会生成3个一样的文件 名为 "card_105_X.png"

# INPUT_DIR: 一个csv文件，记录了所有卡牌信息，可以直接从V0.6规则中的“导出视图”复制粘贴过来
# OUTPUT_DIR: 输出路径，最好是一个空文件夹
# INITIAL_DECK_SETTING: 一个txt文件，记录了玩家初始套牌有哪些卡，格式如："101:6,102:4,103:2"
# CARDBACK_DIR: 牌背png图像


# 注意：
# 卡牌插图会固定读取路径为"Images/CardIcon/XXX.png"的图片，其中XXX为卡牌数字ID。
# 卡牌底板在"Images/CardTemplate"文件夹中，会读取卡牌的派系名称，并在此文件夹中找到对应图片作为底板，可以替换这些图片文件但不要改名。

# 参数
TTS_DE_MODE = True
INPUT_DIR = "../data/cardInfo.csv"
INITIAL_DECK_SETTING = "../data/initialDeck.txt"
OUTPUT_DIR = "../output/v0.603/"
CARDBACK_DIR = "../data/back.png"

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


with open(INPUT_DIR, newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # 跳过第一行，即标题行
    completed = 0

    if not os.path.exists(os.path.join(OUTPUT_DIR, "market")):
        os.mkdir(os.path.join(OUTPUT_DIR, "market"))
    if not os.path.exists(os.path.join(OUTPUT_DIR, "onBoard")):
        os.mkdir(os.path.join(OUTPUT_DIR, "onBoard"))
    if not os.path.exists(os.path.join(OUTPUT_DIR, "initialDeck")):
        os.mkdir(os.path.join(OUTPUT_DIR, "initialDeck"))

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
        if TTS_DE_MODE:
            if row[2] == "常驻":
                outputDir = os.path.join(
                    OUTPUT_DIR,
                    "onBoard",
                    "{0:0>2}x card_{1}.png".format(repeatCount, cardID),
                )
                GenImage(imageInfo, outputDir)
            else:
                outputDir = os.path.join(
                    OUTPUT_DIR,
                    "market",
                    "{0:0>2}x card_{1}.png".format(repeatCount, cardID),
                )
                GenImage(imageInfo, outputDir)

            # 生成初始卡组
            if cardID in initialDeckDict.keys():
                outputDir = os.path.join(
                    OUTPUT_DIR,
                    "initialDeck",
                    "{0:0>2}x card_{1}.png".format(initialDeckDict[cardID], cardID),
                )
                GenImage(imageInfo, outputDir)

        else:
            for i in range(repeatCount):
                outputDir = os.path.join(
                    OUTPUT_DIR, "card_{0}_{1}.png".format(cardID, i + 1)
                )
                GenImage(imageInfo, outputDir)
        completed += 1

    # 卡背png图像
    if TTS_DE_MODE:
        copyfile(CARDBACK_DIR, os.path.join(OUTPUT_DIR, "market", "00 Back.png"))
        copyfile(CARDBACK_DIR, os.path.join(OUTPUT_DIR, "onBoard", "00 Back.png"))
        copyfile(CARDBACK_DIR, os.path.join(OUTPUT_DIR, "initialDeck", "00 Back.png"))

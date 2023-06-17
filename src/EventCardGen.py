from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
import textwrap
import csv
import os
from pathlib import Path
from pprint import pprint

from src.tools import Config, PasteImageInTTSFormat

class EventImageInfo:
    def __init__(self, season, eventType, name, description, eventID):
        self.season = season
        self.eventType = eventType
        self.name = name
        self.description = description
        self.eventID = eventID


def GenEventImage(info: EventImageInfo, outputDir: str, config: Config):
    font = config.font

    def DrawText(text, fontsize, xy, colorRGB, anchor):
        usingFont = font.font_variant(size=fontsize)
        draw.text(xy, text, fill=colorRGB, font=usingFont, anchor=anchor)

    def DrawMultilineText(text, fontsize, xy, colorRGB, anchor):
        lines = textwrap.wrap(text, width=16)
        y_text = xy[1]
        for line in lines:
            # print(line)
            bbox = font.getbbox(line)
            height = fontsize
            DrawText(line, fontsize, (xy[0], y_text), colorRGB, anchor)
            y_text += height * 1.25

    if info.season == 1:
        backTemplateCode = "Back1"
        frontTemplateCode = "Front1"
        nameColor = (30, 27, 92)
        descriptionColor = (52, 100, 135)
        eventTypeColor = (46, 129, 62)
    elif info.season == 2:
        backTemplateCode = "Back2"
        frontTemplateCode = "Front2"
        nameColor = (30, 27, 92)
        descriptionColor = (52, 100, 135)
        eventTypeColor = (46, 129, 62)
    elif info.season == 3:
        backTemplateCode = "Back3"
        frontTemplateCode = "Front3"
        nameColor = (30, 27, 92)
        descriptionColor = (52, 100, 135)
        eventTypeColor = (46, 129, 62)
    else:
        raise AssertionError("Season Number Invalid Error")

    cardTemplateFolder = Path(config.data_dir) / "CardTemplate" / "Event"
    frontTemplateFullDir = cardTemplateFolder / f"{frontTemplateCode}.png"

    img = Image.open(frontTemplateFullDir)
    draw = ImageDraw.Draw(img)

    # classText
    DrawText(info.name, 88, (626, 75), nameColor, "mt")
    DrawText(info.eventType, 56, (901, 150), eventTypeColor, "lt")
    DrawMultilineText(info.description, 60, (135, 272), descriptionColor, "lt")

    if outputDir:
        img.save(outputDir)
    return img


def convert_to_event_images(config_file: str):
    config = Config(config_file)
    pprint(config.to_dict())

    # 参数
    GEN_MODE = config.gen_mode
    INPUT_CSV_FILE = config.input_event_csv_filepath
    OUTPUT_DIR = config.output_dir_with_version
    DATA_DIR = config.data_dir

    with open(INPUT_CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # 跳过第一行，即标题行
        completed = 0

        if not os.path.exists(OUTPUT_DIR):
            Path(OUTPUT_DIR).mkdir()

        if GEN_MODE == "ttsde":
            if not os.path.exists(os.path.join(OUTPUT_DIR, "season1")):
                os.mkdir(os.path.join(OUTPUT_DIR, "season1"))
            if not os.path.exists(os.path.join(OUTPUT_DIR, "season2")):
                os.mkdir(os.path.join(OUTPUT_DIR, "season2"))
            if not os.path.exists(os.path.join(OUTPUT_DIR, "season3")):
                os.mkdir(os.path.join(OUTPUT_DIR, "season3"))
        elif GEN_MODE == "tts":
            imgListSeason1 = []
            imgListSeason2 = []
            imgListSeason3 = []
            if not os.path.exists(os.path.join(OUTPUT_DIR, "atlas")):
                os.mkdir(os.path.join(OUTPUT_DIR, "atlas"))
        else:
            if not os.path.exists(os.path.join(OUTPUT_DIR, "eventRaw")):
                os.mkdir(os.path.join(OUTPUT_DIR, "eventRaw"))

        for row in reader:
            # 处理每一行数据 type, classText, sunCost, coinCost, name, desciption, cardID
            print("{0} {1}".format(completed, row))
            name = row[0]
            season = int(row[1])
            eventType = row[2]
            description = row[3]
            eventID = row[4]

            eventInfo = EventImageInfo(season, eventType, name, description, eventID)
            # ttsde模式: 生成单独的图像 名称为 "03x card_123.png"，用于在tts deck editor中处理
            if GEN_MODE == "ttsde":
                # TODO:待补充tts_de模式的事件生成
                pass

            # tts模式：直接生成少数几张模板，每张模板为10x7，最后一张是牌背的tts导入格式。
            elif GEN_MODE == "tts":
                outputDir = os.path.join(
                    OUTPUT_DIR, f"season{season}", f"01x card_{eventID}.png"
                )
                image = GenEventImage(eventInfo, "", config)
                if season == 1:
                    imgListSeason1.append(image)
                elif season == 2:
                    imgListSeason2.append(image)
                elif season == 3:
                    imgListSeason3.append(image)

            # raw模式：生成若干图像，每张图像对应现实中的一张卡，方便打印（或许）
            else:
                outputDir = os.path.join(
                    OUTPUT_DIR, "eventRaw", "event_{0}.png".format(eventID)
                )
                GenEventImage(eventInfo, outputDir, config)
                pass

            completed += 1

        # 后处理

        # 卡背 png 图像
        if GEN_MODE == "ttsde":
            pass

        # 拼接atlas大图并保存
        elif GEN_MODE == "tts":
            print("正在拼接大图，请稍等....")
            backImgFolder = DATA_DIR / "CardTemplate" / "Event"
            backImg1 = Image.open(backImgFolder / "Back1.png")
            backImg2 = Image.open(backImgFolder / "Back2.png")
            backImg3 = Image.open(backImgFolder / "Back3.png")
            batchimgList1 = PasteImageInTTSFormat(imgListSeason1, backImg1, 3, 5)
            batchimgList2 = PasteImageInTTSFormat(imgListSeason2, backImg2, 3, 5)
            batchimgList3 = PasteImageInTTSFormat(imgListSeason3, backImg3, 3, 5)
            for i in range(len(batchimgList1)):
                outputDir = os.path.join(
                    OUTPUT_DIR, "atlas", "EventS1_{0}.png".format(i + 1)
                )
                batchimgList1[i].save(outputDir)
            print("1/3")
            for i in range(len(batchimgList2)):
                outputDir = os.path.join(
                    OUTPUT_DIR, "atlas", "EventS2_{0}.png".format(i + 1)
                )
                batchimgList2[i].save(outputDir)
            print("2/3")
            for i in range(len(batchimgList3)):
                outputDir = os.path.join(
                    OUTPUT_DIR, "atlas", "EventS3_{0}.png".format(i + 1)
                )
                batchimgList3[i].save(outputDir)
            print("3/3")
            print("拼接完成")

            backImg1.save(os.path.join(OUTPUT_DIR, "atlas", "EventBackS1.png"))
            backImg2.save(os.path.join(OUTPUT_DIR, "atlas", "EventBackS2.png"))
            backImg3.save(os.path.join(OUTPUT_DIR, "atlas", "EventBackS3.png"))


if __name__ == "__main__":
    default_config_path = Config.get_default_config_path()
    convert_to_event_images(default_config_path)

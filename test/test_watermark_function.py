from src.tools import WaterMarkProcess
from PIL import Image

def test_write_file():
    wmp = WaterMarkProcess()
    wmp.add_single_file("./test/test.png", "./test/wm_added.png")


def test_get_PIL_image():
    wmp = WaterMarkProcess()
    img = Image.open("./test/card_103_2.png")
    embed = wmp.add_wm(img) 
    embed.save("embed.png")

    extract_from_img = wmp.extract_wm_from_pil_image(embed, 231)
    print("extract wm from pil image: ", extract_from_img)

    extract_from_file = wmp.extract_wm_from_file("embed.png", 231)
    print("extract wm from file, water mark is: ", extract_from_file)

if __name__ == "__main__":
    test_get_PIL_image()
from src.tools import WaterMarkProcess


if __name__ == "__main__":
    wmp = WaterMarkProcess()
    wmp.add_single_file("./test/test.png", "./test/wm_added.png")
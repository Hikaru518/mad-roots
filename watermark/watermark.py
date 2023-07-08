from blind_watermark import WaterMark
import argparse
import os


def get_alldirectories(folder):
    subdirectories = []
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            subdirectories.append(os.path.join(root, dir))
    subdirectories.append(folder)
    all_directories = []
    for subdirectory in subdirectories:
        all_directories.append(subdirectory[len(folder) :])
    all_directories.sort(key=len)
    return all_directories


def add_watermark(file: str, input: str, output: str) -> None:
    if not file.endswith(".jpg") and not file.endswith(".png"):
        return
    input_file = os.path.join(input, file)
    if not os.path.exists(input_file):
        print("add file not found", input_file)
        return
    if not os.path.exists(output):
        os.makedirs(output)
    print("adding watermark to " + input_file)
    # read the picture
    bwm = WaterMark(password_img=2023, password_wm=2023)
    bwm.read_img(input_file)
    # read the watermark
    watermark = "PEANUX_VAPOURBOX_2023_DICECON"
    bwm.read_wm(watermark, mode="str")
    # embed the watermark
    output_img = os.path.join(output, file)
    bwm.embed(output_img)
    len_wm = len(bwm.wm_bit)
    # check if len_wm.txt exists
    if not os.path.exists(input + "/len_wm.txt"):
        # make a new file
        with open(input + "/len_wm.txt", "w") as f:
            f.write(file + " " + str(len_wm) + "\n")
    else:
        with open(input + "/len_wm.txt", "a") as f:
            f.write(file + " " + str(len_wm) + "\n")
    print("put down the length of wm_bit {len_wm}".format(len_wm=len_wm))
    print("watermark added to " + file)


def extract_watermark(file: str, watermark_length: int) -> None:
    if not file.endswith(".jpg") and not file.endswith(".png"):
        return
    if not os.path.exists(file):
        print("extract file not found", file)
        return
    print("extracting watermark from " + file)
    # read the picture
    bwm = WaterMark(password_img=2023, password_wm=2023)
    wm_extract = bwm.extract(file, wm_shape=watermark_length, mode="str")
    print("watermark is ", wm_extract)


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
    if args.add != "" and args.out != "":
        input_directory = os.path.join(current_directory, args.add)
        output_directory = os.path.join(current_directory, args.out)
        all_directories = get_alldirectories(input_directory)
        for directory in all_directories:
            subdirectory = os.path.join(input_directory, directory)
            print("looking into " + subdirectory)
            for file in os.listdir(subdirectory):
                if file.endswith("/"):
                    continue
                add_watermark(
                    file,
                    os.path.join(input_directory, directory),
                    os.path.join(output_directory, directory),
                )
    elif args.extract != "" and args.watermark_length != 0:
        extract_file = os.path.join(current_directory, args.extract)
        extract_watermark(extract_file, args.watermark_length)
    else:
        print(
            "invalid arguments, input add dir + out dir or extract image + watermark length"
        )

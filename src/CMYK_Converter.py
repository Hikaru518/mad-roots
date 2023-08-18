from PIL import Image
import os
# 打开源图像

rgb_scale = 255
cmyk_scale = 255


def rgb_to_cmyk(r,g,b):
    if (r == 0) and (g == 0) and (b == 0):
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0,255] -> cmy [0,1]
    Rn = r / float(rgb_scale)
    Gn = g / float(rgb_scale)
    Bn = b / float(rgb_scale)

    # extract out k [0,1]
    ma = max(Rn, Gn, Bn)
    k = 1 - ma
    c = 1 - Rn / ma
    m = 1 - Gn / ma
    y = 1 - Bn / ma

    # rescale to the range [0,cmyk_scale]
    return round(c*cmyk_scale), round(m*cmyk_scale), round(y*cmyk_scale), round(k*cmyk_scale)

def normalize_cmyk(cmykColor, oldMax, newMax):
    #print(cmykColor, "old")
    mult = newMax / oldMax
    return round(cmykColor[0] * mult), round(cmykColor[1] * mult), round(cmykColor[2] * mult), round(cmykColor[3] * mult)

def cmyk_to_rgb(c,m,y,k):
    """
    """
    r = rgb_scale*(1.0-(c+k)/float(cmyk_scale))
    g = rgb_scale*(1.0-(m+k)/float(cmyk_scale))
    b = rgb_scale*(1.0-(y+k)/float(cmyk_scale))
    return r,g,b

def ConvertToCMYK(inputDir, outPutDir):
    image = Image.open(inputDir)
    cmyk_image = image.convert('CMYK')      # Convert to CMYK
    cmyk_image.save(outPutDir, 'tiff')


def ConvertFolderToJpeg(inputDir, outputDir):
    count = 0
    os.makedirs(outputDir, exist_ok=True)
    for root, dirs, files in os.walk(inputDir):
        for file in files:
            # 检查文件扩展名是否为.png
            if file.lower().endswith('.png'):

                # if count >= 5:
                #     return
                count += 1

                # 构建输入文件的完整路径
                inputPath = os.path.join(root, file)

                # 构建输出文件的相对路径
                relativePath = os.path.relpath(inputPath, inputDir)
                outputPath = os.path.join(outputDir, os.path.splitext(relativePath)[0] + '.tiff')

                if not os.path.exists(os.path.dirname(outputPath)):
                    os.makedirs(os.path.dirname(outputPath), exist_ok=True)
                # 调用ConvertToJpeg函数将图像转换为JPEG并保存到输出路径
                ConvertToCMYK(inputPath, outputPath)

if __name__ == "__main__":
    # INPUT_DIR = "D:/MadRoots/Repository/mad-roots/output/v0.12.2(Dicecon)/cardRaw"
    # OUTPUT_DIR = "D:/MadRoots/Repository/mad-roots/output/v0.12.2(Dicecon)/cardRawCMYK"

    INPUT_DIR = "G:/MadRoots/Dicecon版本/a"
    OUTPUT_DIR = "G:/MadRoots/Dicecon版本/aCMYK"
    ConvertFolderToJpeg(INPUT_DIR, OUTPUT_DIR)
import os
import glob
import subprocess
from PIL import Image, ImageDraw
from PIL import ImageFilter
from PIL import ImageEnhance
from typing import Tuple
import numpy as np

def apply_effect(image: Image, resolution: Tuple[int, int]) -> Image:
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    width, height = image.size
    target_width, target_height = resolution
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height
    # Convert To Center
    # if aspect_ratio > target_aspect_ratio:
        # # Image is wider than target resolution
        # new_height = int(target_width / aspect_ratio)
        # image = image.resize((target_width, new_height))
        # offset = (0, (target_height - new_height) // 2)
    # else:
        # # Image is taller than target resolution
        # new_width = int(target_height * aspect_ratio)
        # image = image.resize((new_width, target_height))
        # offset = ((target_width - new_width) // 2, 0)
        
    # Full Screen Cropping
    if aspect_ratio > target_aspect_ratio:
        # 如果图像比目标分辨率更宽 If the image is wider than the target resolution
        new_height = int(target_width / aspect_ratio)  # 计算新的高度，保持宽高比不变 Calculate the new height, leaving the aspect ratio unchanged
        new_width = target_width  # 设定目标宽度 Set target width
        if new_height < target_height:
            new_height = target_height
            new_width = int(new_height * aspect_ratio)  # 如果新高度小于目标高度，则根据新高度重新计算宽度 If the new height is less than the target height, the width is recalculated based on the new height     
        image = image.resize((new_width, new_height))  # 调整图像大小为新宽度和新高度 Resize the image to new width and new height
        offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)  # 计算在背景中居中的偏移量 Calculates the offset centered in the background
    else:
        # 如果图像比目标分辨率更高或者宽高比相等 If the image has a higher resolution than the target or an equal aspect ratio
        new_width = int(target_height * aspect_ratio)  # 计算新的宽度，保持宽高比不变 Calculate the new width, leaving the aspect ratio unchanged
        new_height = target_height  # 设定目标高度 Set target altitude
        if new_width < target_width:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)  # 如果新宽度小于目标宽度，则根据新宽度重新计算高度 If the new width is less than the target width, the height is recalculated based on the new width
        image = image.resize((new_width, new_height))  # 调整图像大小为新宽度和新高度 Resize the image to new width and new height
        offset = ((target_width - new_width) // 2, (target_height - new_height) // 2)  # 计算在背景中居中的偏移量 Calculates the offset centered in the background

    # image.show()
    # Add black bars
    background = Image.new("RGBA", resolution, (0,0,0,1))
    background.paste(image, offset)
    # Create Gaussian Blur
    background = background.filter(ImageFilter.GaussianBlur(radius=min(width,height)/8))
    # alpha = background.split()[3]
    # # Normalize the alpha values
    # alpha = Image.eval(alpha, lambda a: 255 * a / 128)
    # # Merge the alpha band back into the image
    # background.putalpha(alpha)
    background.paste(image, offset)
    background = background.convert('RGBA')
    color_layer = Image.new("RGBA", resolution, color_avg(image))
    composite = Image.alpha_composite(color_layer, background)
    return composite

def color_avg(image: Image) -> Tuple[int, int, int]:
    pixels = np.array(image)
    return tuple(map(int, np.average(pixels, axis=(0, 1))))

# Define the configuration file
config_file = "config.txt"

# Read the configuration file
with open(config_file, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()
    target_resolution = tuple(map(int, lines[0].split(',')))
    input_dir = lines[1]
    output_dir = lines[2]
    ini_file = lines[3]

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get a list of all images in the input directory
output_files_dds = all_files = glob.glob(output_dir + '/**/*.*', recursive=True)
output_files_dds = [file for file in output_files_dds if '\\-' not in file]

with open(ini_file, "r", encoding="utf-8") as f:
    ini_lines = f.readlines()
with open(ini_file, "w", encoding="utf-8") as f:
    outputScriptFlag = 0
    for line in ini_lines:
        if line.startswith("global $n_imgs"):
            line = f"global $n_imgs = {len(output_files_dds)}\n"
        if outputScriptFlag == 0:
            f.write(line)
            if line.startswith(";BEGIN_SCRIPT_GENERATED_SECTION"):
                outputScriptFlag = 1
            if line.startswith(";BEGIN_pst85_SCRIPT_GENERATED_SECTION"):
                outputScriptFlag = 2
            if line.startswith(";BEGIN_ResourceLS"):
                break
        else:
            if line.startswith("[") or line.startswith(";BEGIN_ResourceLS") :
                if outputScriptFlag == 1:
                    for i in range(len(output_files_dds)):
                        f.write(f"else if $is_load_prev && $curr_img == {i}\n")
                        f.write(f"	this = ResourceLS.{i}\n")
                    f.write("endif\n\n")
                if outputScriptFlag == 2:
                    for i in range(len(output_files_dds)):
                        f.write(f"else if $is_load_prev && $curr_img == {i}\n")
                        f.write(f"	ps-t85 = ResourceLS.{i}\n")
                    f.write("endif\n\n")
                f.write(line)
                outputScriptFlag = 0
            if line.startswith(";BEGIN_ResourceLS") :
                 break
    for i, output_file_dds in enumerate(output_files_dds):
        f.write(f"[ResourceLS.{i}]\n")
        output_file_dds_windows = output_file_dds.replace('/', '\\')
        f.write(f"filename = {output_file_dds_windows}\n")

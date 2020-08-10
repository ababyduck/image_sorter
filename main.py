import os
import shutil
import sys
from PIL import Image

COMMON_RATIOS = ["16:9", "16:10", "8:5", "5:4", "4:3"]
MIN_WIDTH = 1920
MIN_HEIGHT = 1080


def is_image(filename):
    image_types = ["jpg", "jpeg", "png", "gif"]
    file_ext = filename.lower().split(".")[-1]
    return os.path.isfile(filename) and file_ext in image_types


def get_aspect_ratio(width, height):
    def gcd(a, b):
        return a if b == 0 else gcd(b, a % b)

    if width == height:
        return "1:1"
    else:
        r = gcd(width, height)
        x = int(width / r)
        y = int(height / r)
        return f"{x}:{y}"


def mk_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


def sanitize_dir_name(dirname):
    replace_dict = {
        ":": "x",
        ">": "_",
        "<": "_",
        "|": "_",
        "*": "_",
        "\"": "'",
    }
    for forbidden_char, new_char in replace_dict.items():
        if forbidden_char in dirname:
            dirname = dirname.replace(forbidden_char, new_char)
    return dirname


class ImageFile:
    """Contains image filename, dimensions, and info about aspect ratio
    """
    def __init__(self, filename):
        img = Image.open(filename)
        self.filename = filename
        self.width, self.height = img.size
        self.aspect = get_aspect_ratio(self.width, self.height)
        self.is_multi_monitor = False
        self.monitor_count = f"Single {self.aspect}"

        if self.aspect not in COMMON_RATIOS:
            for ratio in COMMON_RATIOS:
                common_rw, common_rh = ratio.split(":")
                my_rw, my_rh = self.aspect.split(":")
                if my_rh == common_rh and int(my_rw) % int(common_rw) == 0:
                    self.is_multi_monitor = True
                    factor = int(my_rw) // int(common_rw)
                    if factor == 2:
                        self.monitor_count = f"{ratio} Dual"
                    elif factor == 3:
                        self.monitor_count = f"{ratio} Triple"
                    else:
                        self.monitor_count = f"{ratio} Other"


def sort_wallpapers(img_path):
    """ Sorts image files of supported type by their aspect ratio
    """
    os.chdir(img_path)
    files = os.listdir(img_path)
    print(files)
    sorted_count = 0

    for file in files:
        if is_image(file):
            img = ImageFile(file)
            aspect = img.aspect
            if img.aspect == "1:1":
                aspect_folder = "Square"
            elif img.height > img.width:
                aspect_folder = "Tall"
            elif MIN_WIDTH and img.width < MIN_WIDTH:
                aspect_folder = f"Width under {MIN_WIDTH}"
            elif img.aspect in COMMON_RATIOS:
                aspect_folder = aspect
            elif img.is_multi_monitor:
                aspect_folder = img.monitor_count
            elif MIN_HEIGHT and img.height < MIN_HEIGHT:
                aspect_folder = f"Height under {MIN_HEIGHT}"
            else:
                # aspect_folder = os.path.join("Weird", aspect)
                aspect_folder = "Weird"

            aspect_folder = sanitize_dir_name(aspect_folder)
            mk_dir(aspect_folder)
            shutil.move(file, os.path.join(aspect_folder, file))
            print(f"\tMoved \"{file}\" into folder \"{aspect_folder}\"")
            sorted_count += 1

    print(f"Sorted {sorted_count} files in {img_path}")


if __name__ == "__main__":
    path = input("Enter a valid path with images to sort them by aspect ratio\n> ")
    while not os.path.isdir(path):
        if path.lower() == "q":
            sys.exit()
        else:
            path = input("Invalid path. Try again or q to quit\n> ")
    sort_wallpapers(path)

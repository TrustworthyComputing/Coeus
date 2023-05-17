import os
import shutil
import sys
import subprocess
import hashlib
import xxhash
import argparse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
#from npzip import npzip
#from npzip import npunzip
from PIL import Image, ImageEnhance

core_path = os.getcwd()

image_path = "img4silhouette/"
silhouette_path = "silhouette4array/"
array_path = "arrays4ffs/"

def rotater(input_path, output_path, angle, category):
    """Pass input stl file and output directory, 
    angle for object to be rotated and what type of object it is"""

    x = 0
    y = 0
    z = 0

    name = 1
    for rot in range(int(((180/int(angle))*3)+3)):
        root_file = os.path.split(input_path)
        root_file = os.path.splitext(root_file[1])
        output_folder = os.path.join(os.getcwd(), image_path)
        output_folder = os.path.join(output_folder, category+"-"+str(root_file[0]))
        try:
            os.mkdir(output_folder)
        except:
            pass

        image_output = os.path.join(output_folder, str(name)+".png")
        if rot <= 180/int(angle):
            rotate_command = """openscad -o ./stl_files/rotated.stl -D 'model="{}"; degrees=[{},0,0]' ./rotate.scad""".format(input_path, int(angle) * x)
            subprocess.run(rotate_command, shell=True)
            take_img_command = """openscad -o {} -D 'model="./stl_files/rotated.stl"; col=[0, 0.55, 0.81]' --autocenter --viewall --colorscheme Nature --imgsize 3000,3000 --camera=0,0,0,0,0,0,10 ./open_stl.scad""".format(image_output)
            subprocess.run(take_img_command, shell=True)
            x+=1
            name+=1
        elif rot <= ((180/int(angle))*2)+1:
            rotate_command = """openscad -o ./stl_files/rotated.stl -D 'model="{}"; degrees=[0,{},0]' ./rotate.scad""".format(input_path, int(angle) * y)
            subprocess.run(rotate_command, shell=True)
            take_img_command = """openscad -o {} -D 'model="./stl_files/rotated.stl"; col=[0, 0.55, 0.81]' --autocenter --viewall --colorscheme Nature --imgsize 3000,3000 --camera=0,0,0,0,0,0,10 ./open_stl.scad""".format(image_output)
            subprocess.run(take_img_command, shell=True)
            y+=1
            name+=1
        else:
            rotate_command = """openscad -o ./stl_files/rotated.stl -D 'model="{}"; degrees=[0,0,{}]' ./rotate.scad""".format(input_path, int(angle) * z)
            subprocess.run(rotate_command, shell=True)
            take_img_command = """openscad -o {} -D 'model="./stl_files/rotated.stl"; col=[0, 0.55, 0.81]' --autocenter --viewall --colorscheme Nature --imgsize 3000,3000 --camera=0,0,0,0,0,0,10 ./open_stl.scad""".format(image_output)
            subprocess.run(take_img_command, shell = True)
            z+=1 
            name+=1

    return output_folder



def silhouette_extraction(input_path, output_path, media_type, num_imgs):
    """Function to call matlab script and pass image folder to matlab, 
    media type is --i for image and --v for video"""

    home_dir = os.getcwd()
    root_file = os.path.split(input_path)
    output_folder = os.path.join(output_path, root_file[1])

    try:
        os.mkdir(output_folder)
    except:
        pass

    os.chdir("/Applications/MATLAB_R2021a.app/bin")
    silhouette_command = '''./matlab -batch "silhouette {} {} {} {}"'''.format(input_path, output_folder, media_type, num_imgs)
    subprocess.run(silhouette_command, shell=True)
    os.chdir(home_dir)
    return(output_folder)


def array_maker_file(img, output_path, category):
    """Pass folder of images to and specify array save location
    Category is for type of object"""
    arrays = []
    try:
        stacked_array = np.array(Image.open(img).convert('L'))
        unique_name = xxhash.xxh3_128(stacked_array).hexdigest().upper()
        name = category + "-" + unique_name + ".npy"
        array_location = os.path.join(output_path, name)
        np.save(array_location, stacked_array)
    except:
        print("Error saving array", img, output_path)
        array_location = ""

    return array_location



def array_maker(input_path, output_path, category):
    """Pass folder of images to and specify array save location
    Category is for type of object"""
    arrays = []
    for file in os.listdir(input_path):
        current_img = os.path.join(input_path, file)
        try:
            img = mpimg.imread(current_img)
            arrays.append(img)
        except:
            print("Error reading image", input_path)
    try:
        stacked_array = np.stack(arrays)
        unique_name = xxhash.xxh3_128(stacked_array).hexdigest().upper()
        name = category + "-" + unique_name + ".npy"
        array_location = os.path.join(output_path, name)
        np.save(array_location, stacked_array)
    except:
        print("Error saving array", input_path, output_path)

    return array_location


def array_tester(arraypath):
    """Search for array passed to function"""
    search_command = """python3 ffs.py --mode search --array {} --print_fine_grained""".format(arraypath)
    subprocess.run(search_command, shell=True)



def array_enrollment(array_file, searchname):
    """Enroll array passed to function"""
    enroll_command = """python3 ffs.py --mode learn --array {} --name {}""".format(array_file, searchname)
    subprocess.run(enroll_command, shell=True)


def image_converter(input_path, output_path):
    count = 0
    for file in os.listdir(input_path):
        count+=1
        source_path = os.path.join(input_path, file)
        filename = "{}.png".format(count)
        output = os.path.join(output_path, filename)
        os.rename(source_path, output)


def shapehd_extractor(input_path, output_path):
    """Used to extract silhouettes from the various folders shapehd outputs"""

    count = 0
    for file in os.listdir(input_path):
        extension = os.path.splitext(file)
        if extension[1] == ".npz" or file == ".DS_Store":
            continue
        else:
            count+=1
            next_path = os.path.join(input_path, file)
            for image in os.listdir(next_path):
                if "pred" in image:
                    image_path = os.path.join(next_path, image)
                    final_path = "silhouette{}.png".format(count)
                    output_folder = os.path.join(output_path, final_path)
                    os.rename(image_path, output_folder)
                else:
                    continue


def image_resizer(input_path):
    """Resize shapehd silhouettes into 1000x1000"""
    for file in os.listdir(input_path):
        if file == ".DS_Store":
            continue
        else:
            image_path = os.path.join(input_path, file)
            image = Image.open(image_path)
            image = image.resize((1000,1000))
            image.save(image_path)



def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode',       help='Learn or Search or Generate mode', type=str.lower, choices=['learn', 'search', 'generate'], required=True)
    parser.add_argument('--file',       help='Path to stl files/directory or path to array for search', required=True)
    parser.add_argument('--num_of_objects',     help='Number of objects to enroll', required=True)
    args = parser.parse_args()
    return args.mode, args.file, args.num_of_objects


def image_enhancer(input_image):
    """Pass input image path and increase contrast and brightness"""

    im = Image.open(input_image)
    enhancer = ImageEnhance.Brightness(im)
    factor = 2
    im_output = enhancer.enhance(factor)
    im_output.save(input_image)
    im = Image.open(input_image)
    enhancer = ImageEnhance.Contrast(im)
    factor = 1.5
    im_output = enhancer.enhance(factor)
    im_output.save(input_image)


def array_names(input_path, category):
    """Used to check which files correspond to which hash names
    takes folder of images and prints out corresponding name"""

    for array in os.listdir(input_path):
        arrays = []
        array_path = os.path.join(input_path, array)
        for img in os.listdir(array_path):

            current_img = os.path.join(array_path, img)

            try:
                img = mpimg.imread(current_img)
                arrays.append(img)
            except:
                pass

        try:
            stacked_array = np.stack(arrays)
            unique_name = xxhash.xxh3_128(stacked_array).hexdigest().upper()
            name = category + "-" + unique_name + ".npy"
            x = "{} -> {}".format(array, name)
        except:
            pass

def image_renamer(input_path):
    x = 1
    for file in os.listdir(input_path):
            path = os.path.join(input_path, file)
            os.rename(path, input_path+"{}".format(x))
            x+=1

def generate_folders():
    """Creates folders needed for program running"""

    image_loc = os.path.join(core_path, image_path)
    silhouette_loc = os.path.join(core_path, silhouette_path)
    array_loc = os.path.join(core_path, array_path)

    if os.path.isdir(image_loc) == True:
        pass
    else:
        os.mkdir(image_loc)

    if os.path.isdir(silhouette_loc) == True:
        pass
    else:
        os.mkdir(silhouette_loc)

    if os.path.isdir(array_loc) == True:
        pass

    else:
        os.mkdir(array_loc)


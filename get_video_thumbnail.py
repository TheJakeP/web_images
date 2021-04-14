import sys
import os
from PIL import Image
import cv2


def check_folder_exists_and_make(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def create_thumbnails_for_videos_in_directory(video_folder, img_dest, thumb_dest):
    for root, dirs, files in os.walk(video_folder + os.sep, topdown=False):
        total = len(files)
        i = 1
        for dirty_name in files:
            create_thumbnail_for_video(dirty_name, video_folder,  img_dest)
            resize_to_thumbnail(dirty_name, img_dest, thumb_dest)
            print("Item", i, "out of:", total)
            i += 1
            
def create_thumbnail_for_video(video_name, origin_dir, save_dir):
    origin_filepath = origin_dir + video_name

    dirty_name = video_name.replace(" ", "")
    dirty_name_arr = dirty_name.split(".")[:-1]
    clean_name = "".join(dirty_name_arr)
    destin_filepath = save_dir + "\\" + clean_name

    if os.path.isfile(origin_filepath):
        vidcap = cv2.VideoCapture(origin_filepath)
        vidcap.set(cv2.CAP_PROP_POS_MSEC, 1500) 
        success,image = vidcap.read()
        if success:
            cv2.imwrite(destin_filepath + ".jpg", image)     # save frame as JPEG file      
            success,image = vidcap.read()
            print('\tSaving Video Frame: ', destin_filepath)


def resize_to_thumbnail(dirty_name, origin_dir, thumb_dest):
    dirty_name = dirty_name.replace(" ", "")
    dirty_name_arr = dirty_name.split(".")[:-1]
    rename = "".join(dirty_name_arr) 

    thumb_dest = thumb_dest + rename +  "_thumb.jpg"

    if os.path.isfile(origin_dir + rename + ".jpg"):
        basewidth = 300
        img = Image.open(origin_dir + rename + ".jpg")
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        img.save(thumb_dest)
        print("\tThumbnail Saved:", thumb_dest)

def main():
    if len(sys.argv) > 1:

        os.chdir("..")
        os.chdir("..")
        cwd = os.getcwd()

        video_folder = str(sys.argv[1])
        video_folder = os.path.join(cwd, video_folder) + os.sep

        img_dest = "img\\videos\\originals"
        img_dest = os.path.join(cwd, img_dest) + os.sep

        thumb_dest = "img\\videos\\thumbnails"
        thumb_dest = os.path.join(cwd, thumb_dest) + os.sep
        
        optimized = ""
        optimized = os.path.join(cwd, optimized) + os.sep

        check_folder_exists_and_make(img_dest)
        check_folder_exists_and_make(thumb_dest)

        create_thumbnails_for_videos_in_directory(video_folder, img_dest, thumb_dest)
    else:
        print("\n\tPlease execute the script with a folder to convert. Ex converter.py /new_folder\n")

main()
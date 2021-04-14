import sys
import os
from PIL import Image

# from imagify import Imagify

class Images:

    #set standard sizes
    preview     =   (700, 700)
    thumbnail   =   (300, 300)

    def __init__(self):

        site_root = self.get_root_directory(2)
        img_dir = os.path.join(site_root, 'img')
        prod_dir = os.path.join(img_dir, "products")


        not_imported = os.path.join(img_dir, "not_imported") + os.sep
        original = os.path.join(prod_dir, "original") + os.sep
        optimized = os.path.join(prod_dir, "optimized") + os.sep
        preview = os.path.join(prod_dir, "preview") + os.sep        
        thumbnail = os.path.join(prod_dir, "thumbnail") + os.sep



        self.destinations = {
            "not_imported"  :   not_imported,
            "original"      :   original,
            "optimized"     :   optimized,
            "preview"       :   preview,
            "thumb"         :   thumbnail,
        }
        self.resize = {
            "thumb"     : self.thumbnail,
            "preview"   : self.preview
        }

        #Make sure folders exist
        self.check_folder_exists_and_make(original)
        self.check_folder_exists_and_make(optimized)
        self.check_folder_exists_and_make(preview)
        self.check_folder_exists_and_make(thumbnail)

        self.convert_folder_to_jpeg(not_imported, original)

    def get_root_directory(self, parents):
        directory = os.getcwd()

        for i in range(0, parents):
            directory = os.path.dirname(directory)
        
        return directory

    def check_folder_exists_and_make(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    def convert_folder_to_jpeg(self, directory, destination):
        for root, dirs, files in os.walk(directory + os.sep, topdown=False):
            total = len(files)
            i = 1
            for original_file_name in sorted(files):
                new_file_name, meta_data = self.get_new_file_name(original_file_name)
                open_path = os.path.join(directory, original_file_name)

                if os.path.isfile(open_path):
                    img = Image.open(open_path)
                    img = img.convert('RGB')
                    data = list(img.getdata())

                    image_without_exif = Image.new(img.mode, img.size)
                    image_without_exif.putdata(data) 
                    img = image_without_exif
                    
                    original    = self.convert_image_to_jpeg(img, open_path, new_file_name)
                    optimized   = self.make_optimized_image(img, open_path, new_file_name)
                    preview     = self.make_resized_image(img, "preview", open_path, new_file_name)
                    thumbnail   = self.make_resized_image(img, "thumb", open_path, new_file_name)
                    
                    self.add_to_database_by_api(meta_data, original, optimized, preview, thumbnail )
                    os.remove(open_path)
                    print("Item Number", i, "out of", total)
                    i += 1

    def add_to_database_by_API(self, meta_data, original, optimized, preview, thumbnail):
        import requests
        import json

        # Checks if local dev environment is Windows
        if os.name == 'nt':
            url = 'http://butterfly.local/api/v0/'
            print("On local environment")
        else:
            url = 'http://api-endpoint.com/api/v0/'

        headers = {
            'Authorization'     : "(some auth code)", 
            'Accept'            : 'application/json', 
            'Content-Type'      : 'application/json',
            'Function'          : 'add_image_to_db',
            }
        if "style" not in meta_data:
            meta_data['style'] = ""

        if "color" not in meta_data:
            meta_data['color'] = ""

        if "view" not in meta_data:
            meta_data['view'] = ""

        dictionary = {
            "style"     : meta_data['style'],
            "color"     : meta_data['color'],
            "view"      : meta_data['view'],
            
            "original"  : self.get_relative_path(original),
            "optimized" : self.get_relative_path(optimized),
            "preview"   : self.get_relative_path(preview),
            "thumbnail" : self.get_relative_path(thumbnail),
        }

        data_payload = json.dumps(dictionary)
        r = requests.post(url, data=data_payload, headers=headers)
        print (r)

    def get_relative_path(self, path):
        path_arr = path.split(os.path.sep)
        cut = path_arr.index("img")
        relative_path = "/" + "/".join(path_arr[cut:])
        return relative_path
        

    def convert_image_to_jpeg(self, img, open_path, new_file_name):
        
        save_path = self.destinations['original']
        save_path = os.path.join(save_path, new_file_name)

        rgb_image = img.convert('RGB')
        rgb_image.save(save_path, "JPEG", quality=100)
        print ("\tConverting:\t\t", save_path)
        return save_path

    def make_optimized_image(self, img, open_path, new_file_name):
        file_arr = new_file_name.split(".")
        file_arr[0] = file_arr[0] +  "_optimized"
        new_file_name = ".".join(file_arr) 

        save_path = self.destinations['optimized']
        save_path = os.path.join(save_path, new_file_name)

        img.save(save_path, quality=30, optimize=True)
        print ("\tOptimizing:\t\t", save_path)
        return save_path


    def make_resized_image(self, img, suffix, open_path, new_file_name):
        file_arr = new_file_name.split(".")
        file_arr[0] = file_arr[0] +  "_" + suffix
        new_file_name = ".".join(file_arr) 

        save_path = self.destinations[suffix]
        save_path = os.path.join(save_path, new_file_name)

        newsize = self.resize[suffix]

        img.thumbnail( newsize, Image.ANTIALIAS )
        img.save(save_path, quality=50, optimize=True)

        print ("\tMaking " + suffix + ":\t\t", save_path)
        return save_path

    

    def get_new_file_name(self, original_name):
        img_arr = original_name.split("_")[:-1]
        meta_data = dict()
        style = ""
        color = ""
        view = ""
        length = len(img_arr)
        if (length >= 1):
            style = img_arr[0]
            meta_data['style'] = img_arr[0]
        if (length >= 2):
            color = "_" + img_arr[1] + "_"
            meta_data['color'] = img_arr[1]
        if (length >= 3):
            view = img_arr[2]
            meta_data['view'] = img_arr[2]

        rename = style + color + view 
        rename = rename.strip("_") + '.jpg'
        rename = rename.lower()

        return rename, meta_data

    def get_command_line_arg_at_index(self, index):
        try:
            i = sys.argv[index]
        except IndexError:
            # print('sorry, no 5')
            print("\n\tScript Missing Parameters. Ex converter.py /new_folder\n")
            quit()
        else:
            return str(i)

    def create_thumbnails(self):
        pass


def main():
    images = Images()


main()
import sys
import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np

import png2array_helper as _ph

def main():

    core_path = os.getcwd()

    image_path = os.path.join(core_path, 'img4silhouette/')
    silhouette_path = os.path.join(core_path, 'silhouette4array/')
    array_path = os.path.join(core_path, 'arrays4ffs/')
    search_path = os.path.join(core_path, 'search4ffs/')

    mode, filepath, num_of_files = _ph.parseargs()

    _ph.generate_folders()

    if mode == 'learn':
        names = []
        cnames = []
        silhouette_folder = []
        #This is the top level direectory
        for file in os.listdir(filepath):
            input_image = os.path.join(filepath, file)
            le_split = file.split('-')

            #File naming convention should be category-stlImageName/batchXXXX/*.png
            #The batch XXXX is generated from MarrNet
            if len(le_split) < 2:
                print("Bad Name:", file, le_split)
                continue
            cname = le_split[0]
            fname = le_split[1]
            for i in range(int(num_of_files)):
                fstr = "batch{:04}/{:04}_05_pred_depth.png".format(i,i) 
                pathname = os.path.join(input_image, fstr)
                if os.path.isfile(pathname):
                    names.append(fname)
                    cnames.append(cname)
                    silhouette_folder.append(pathname)
                else:
                    print("Bad File:", pathname)

        array_folder = []
        i = 0
        for sfile in silhouette_folder:
            array_folder.append(_ph.array_maker_file(sfile, array_path, cnames[i]))
            i+=1
        i = 0
        for afile in array_folder:
            print(afile, cnames[i], names[i])
            _ph.array_enrollment(afile, cnames[i]+"-"+names[i])
            i+=1

    elif mode == 'search':
        names = []
        for file in os.listdir(filepath):
            input_image = os.path.join(filepath, file)
            le_split = file.split('-')
            #File naming convention should be category-stlImageName/batchXXXX/*.png
            #The batch XXXX is generated from MarrNet
            if len(le_split) < 2:
                print("Bad Name:", file, le_split)
                continue
            cname = le_split[0]
            fname = le_split[1]
            silhouette_folder = []
            test = np.arange(180)
            for i in range(int(num_of_files)):
                fstr = "batch{:04}/{:04}_05_pred_depth.png".format(test[i],test[i])
                pathname = os.path.join(input_image, fstr)
            if os.path.isfile(pathname):
                names.append(fname)
                silhouette_folder.append(pathname)
            else:
                print("Bad File:", pathname)


            array_folder = []
            i = 0
            sfiles_str = ""
            for sfile in silhouette_folder:
                sfiles_str += sfile
                sfiles_str += " "
                i+=1
                array_folder.append(_ph.array_maker_file(sfile, array_path, cname))

            i = 0
            afiles_str = ""
            print(cname+"-"+fname, end='', flush=True)
            for afile in array_folder:
                afiles_str += afile
                afiles_str += " "
                i+=1
            _ph.array_tester(afiles_str)

    else: #mode == generate
        for file in os.listdir(filepath):
            image = os.path.join(filepath, file)
            _ph.image_enhancer(image)
            silhouette_folder = _ph.silhouette_extraction(filepath, silhouette_path, "--i", "30")
            array_path = _ph.array_maker(silhouette_folder, array_path, category)
            _ph.array_tester(array_path)

main()


"""Replacing spaces (or other charater) of file/folder names and inside the Rmd files
for the sharestats project

Specify the <folder> as argument to run this script

O. Lindemann
"""

import os
import sys
from os.path import join, splitext


def rmd_replace_names(rmd_file_path, rename_list):
    txt = []
    change_required = False
    with open(rmd_file_path, 'r') as fl:
        for line in fl.readlines():
            for old_name, new_name in rename_list:
                if line.find(old_name) >= 0:
                    change_required = True
                    line = line.replace(old_name, new_name)
                if old_name.lower().endswith(".rmd"):
                    # replace name of question, that is, filename without ".rmd"
                    if line.find(old_name[:-4]) >= 0:
                        change_required = True
                        line = line.replace(old_name[:-4], new_name[:-4])
            txt.append(line)

    if change_required:
        print("changing {}".format(rmd_file_path))
        with open(rmd_file_path, 'w') as fl:
            fl.writelines(txt)

    return change_required


def rename(path, source_chr=" ", destination_chr="-", folder=False):
    # recursive function. First files then folder
    for (dirpath, dirnames, filenames) in os.walk(path):
        if folder:
            names = dirnames
        else:
            names = filenames

        # make rename list
        rename_list = []
        for name in names:
            new = name.replace(source_chr, destination_chr)
            if name != new:
                rename_list.append((name, new))

        if len(rename_list) == 0:
            continue

        if not folder:
            for name in names:
                if name.lower().endswith(".rmd"):
                    rmd_replace_names(join(dirpath, name), rename_list)

        # rename files/Folder
        for old, new in rename_list:
            old = join(dirpath, old)
            new = join(dirpath, new)
            print("rename {} -> {}".format(old, new))
            os.rename(old, new)

    if not folder:
        rename(path, source_chr=source_chr, destination_chr=destination_chr, folder=True)


if __name__ == "__main__":
    print("Folder: {}".format(sys.argv[1]))
    rename(path = sys.argv[1],
            source_chr=" ",
            destination_chr="-", )


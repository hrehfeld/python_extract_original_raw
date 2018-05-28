import os

from pathlib import Path
from collections import OrderedDict as odict

from subprocess import check_call, check_output

import shutil

from datetime import datetime

def copy_filestamp(image_filepath, out_filepath):
    times = image_filepath.stat()
    os.utime(str(out_filepath), times=(times.st_atime, times.st_mtime))
    

delete_file = Path('delete_list')
warnings_file = Path('warnings')

import sys


base_dir = Path(sys.argv[1])

with warnings_file.open('a') as warnings:
    for image_filepath in base_dir.glob('**/*.dng'):
        print(image_filepath)
        cmd = ['exiftool', '-*original*raw*image*', image_filepath]
        out = check_output(cmd).decode('utf-8')
        if out.startswith('Original Raw Image              :'):

            cmd = ['exiftool', '-*original*raw*file*name*', str(image_filepath)]
            out_filepath = check_output(cmd, stderr=warnings).decode('utf-8')

            prefix = 'Original Raw File Name          : '

            assert(out_filepath.startswith(prefix))
            out_filepath = out_filepath[len(prefix):].strip()
            out_filepath = image_filepath.parent / out_filepath

            print(out_filepath)
            if out_filepath.exists():
                raise Exception(out_filepath)

            with out_filepath.open('wb') as f:
                cmd = ['exiftool', '-b', '-original*raw*image*', str(image_filepath)]
                out = check_call(cmd, stdout=f)

            copy_filestamp(image_filepath, out_filepath)

            xmp_filepath_old = image_filepath.with_suffix('.xmp')
            if not xmp_filepath_old.exists():
                print(xmp_filepath_old)
                cmd = ['exiftool', '-tagsFromFile', str(image_filepath), str(xmp_filepath_old)]
                out = check_call(cmd)
                copy_filestamp(image_filepath, xmp_filepath_old)

            xmp_filepath = image_filepath.with_suffix(image_filepath.suffix + '.xmp')
            xmp_filepath_new = out_filepath.with_suffix(out_filepath.suffix + '.xmp')
            if xmp_filepath.exists():
                print(xmp_filepath, xmp_filepath_new)
                shutil.copy(str(xmp_filepath), str(xmp_filepath_new))
                copy_filestamp(xmp_filepath, xmp_filepath_new)
                xmp_filepath.unlink()

            image_filepath.unlink()
            print(image_filepath)



#!/usr/bin/python
#
# This script change python caffe symbolic link according to the
# target caffe root path.
# This script is used to quick switch the different version of caffe

import sys
import os
import glog as log


def create_link(dst, link, hardlink=False):
    if os.path.exists(dst) is not True:
        log.error('\033[01;31mERROR\033[0m: Can not find %s' % dst)
        return False
    if os.path.exists(link):
        log.warn('Delete the original link %s --> %s' %
                 (link, os.readlink(link)))
        try:
            os.remove(link)
        except:
            log.error('\033[01;31mERROR\033[0m: Can not remove \
\033[33m%s\033[0m' % link)

    log.info('Create %s --> %s' % (link, dst))
    if hardlink:
        try:
            os.link(dst, link)
        except:
            log.error('\033[01;31mERROR\033[0m: \
Create Hard link error %s --> %s' % (link, dst))
            log.error('Create Symlink instead')
            os.symlink(dst, link)
    else:
        os.symlink(dst, link)
    return True


def main(argv):
    help_msg = 'caffe_select.py <caffe_root>'
    pypath = r'/home/nile/pymodels/'
    libpath = r'/home/nile/lib/'
    binpath = r'/home/nile/bin/'
    try:
        caffe_root = argv[0]
    except:
        print help_msg
        sys.exit(2)
    # Check if the caffe_root is exist
    if os.path.exists(caffe_root) is not True:
        print help_msg
        print 'Can not find the target path'
        sys.exit(2)

    caffe_root = os.path.abspath(caffe_root)
    # change the python caffe module
    pylink = pypath + 'caffe'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'python/caffe'
    else:
        pymodule = caffe_root + r'/python/caffe'
    create_link(pymodule, pylink)
    # change the caffe lib
    pylink = libpath + 'libcaffe.so'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'build/lib/libcaffe.so'
    else:
        pymodule = caffe_root + r'/build/lib/libcaffe.so'
    create_link(pymodule, pylink)
    # change the caffe bin
    pylink = binpath + 'caffe'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'build/tools/caffe'
    else:
        pymodule = caffe_root + r'/build/tools/caffe'
    create_link(pymodule, pylink)
    # change the convert_imageset
    pylink = binpath + 'convert_imageset'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'build/tools/convert_imageset'
    else:
        pymodule = caffe_root + r'/build/tools/convert_imageset'
    create_link(pymodule, pylink)
    # change the compute_image_mean
    pylink = binpath + 'compute_image_mean'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'build/tools/compute_image_mean'
    else:
        pymodule = caffe_root + r'/build/tools/compute_image_mean'
    create_link(pymodule, pylink)

    # change the plot_training_log
    pylink = binpath + 'plot_training_log.py'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'tools/extra/plot_training_log.py.example'
    else:
        pymodule = caffe_root + r'/tools/extra/plot_training_log.py.example'
    create_link(pymodule, pylink)

    # change the parse_log
    pylink = binpath + 'parse_log.py'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'tools/extra/parse_log.py'
    else:
        pymodule = caffe_root + r'/tools/extra/parse_log.py'
    create_link(pymodule, pylink)

    # change the parse_log
    pylink = binpath + 'parse_log.sh'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'tools/extra/parse_log.sh'
    else:
        pymodule = caffe_root + r'/tools/extra/parse_log.sh'
    create_link(pymodule, pylink)

    # change the extract_seconds
    pylink = binpath + 'extract_seconds.py'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'tools/extra/extract_seconds.py'
    else:
        pymodule = caffe_root + r'/tools/extra/extract_seconds.py'
    create_link(pymodule, pylink)

    # change the summarize
    pylink = binpath + 'summarize.py'
    if caffe_root[-1] == '/':
        pymodule = caffe_root + r'tools/extra/summarize.py'
    else:
        pymodule = caffe_root + r'/tools/extra/summarize.py'
    create_link(pymodule, pylink)


if __name__ == "__main__":
    main(sys.argv[1:])

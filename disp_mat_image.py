#!/usr/bin/python

# This script read a mat file and try to show the images contained
# in the mat file

import getopt
import image_tools
import log_tools
import sys
import imshow_lib
import matlab_tools


def main(argv):
    in_file = None
    var_name = None

    is_transpose = False

    help_msg = 'disp_mat_image.py -i <mat> -v [var]\n\
-i <mat>        The input mat file\n\
-v [var]        The var name in the mat\n\
-t              Transpose the image before display'

    try:
        opts, args = getopt.getopt(argv, 'hi:v:t')
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt == '-i':
            in_file = arg
        elif opt == '-v':
            var_name = arg
        elif opt == '-t':
            is_transpose = True

    if in_file is None:
        print help_msg
        sys.exit()

    im = matlab_tools.load_mat(in_file, var_name)
    im = image_tools.preprocess(im)
    if is_transpose:
        if len(im.shape) == 2:
            im = im.transpose()
        elif len(im.shape) == 3:
            im = im.transpose([1, 0, 2])
        else:
            log_tools.log_err('Can not display the image with \
shape %s' % str(im.shape))

    ish = imshow_lib.Imshow()
    ish.autoshow(im)
    raw_input('Press Enter to exist ...')


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/python

# This script read a mat file and try to show the images contained
# in the mat file

import getopt
import sys
import imshow_lib
import matlab_tools


def main(argv):
    in_file = None
    var_name = None

    help_msg = 'disp_mat_image.py -i <mat> -v [var]\n\
-i <mat>        The input mat file\n\
-v [var]        The var name in the mat'

    try:
        opts, args = getopt.getopt(argv, 'hi:v:')
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

    if in_file is None:
        print help_msg
        sys.exit()

    im = matlab_tools.load_mat(in_file, var_name)
    ish = imshow_lib.Imshow()
    ish.imshow(im)

    raw_input('Press Enter to exist ...')


if __name__ == '__main__':
    main(sys.argv[1:])

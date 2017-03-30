#!/usr/bin/python

# This script will load the pased log file (parsed by the parse_log.py or
# parse_log.sh, and plot the train or test curve

import getopt
import sys
import matplotlib.pyplot as plt
# Load the caffe plot lib
import plot_training_log as pl


def main(argv):
    # Define the cols of the X and Y label in the parsed log file
    # The iter number
    DEF_X = 0
    # The loss
    DEF_Y = 2

    in_file = None
    out_file = None

    help_msg = 'plot_parsed_log.py -i <log> -o [jpg]\n\
-i <log>        The caffe log file created by parse_log.sh\n\
-o [jpg]        The output jpg file.'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:')
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt == '-i':
            in_file = arg
        elif opt == '-o':
            out_file = arg

    if in_file is None:
        print help_msg
        sys.exit()

    # Load the data
    data = pl.load_data(in_file, DEF_X, DEF_Y)
    plt.ion()
    plt.plot(data[0], data[1], linewidth=0.75)
    if out_file is not None:
        plt.savefig(out_file)
    plt.pause(0.1)
    plt.ioff()


if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/python

# This script load the caffe prototype and the caffemodel, it
# can set the certain conv layer filter to gaussian filter and save
# the model into a new caffemodel file
# Note:
#   Normally the param blob have more than 1 channels, in that case
#   it will set gaussian to all the channels of the param blob if the
#   channel number is not set

import getopt
import sys
import glog as log
import numpy as np
import caffe
import crash_on_ipy


def main(argv):
    I = log.info
    proto_file = None
    caffemodel_file = None
    out_file = None
    param_name = None

    channel_idx = None

    help_msg = 'set_gaussian_filter -p <prototxt> -o <caffemodel> \
-m [caffemodel] -v [param] \n\
-p <prototxt>           The prototxt file.\n\
-o <caffemodel>         The output caffemodel.\n\
-m [caffemodel]         The caffemodel should be modified.\n\
-v [param]              The conv param blob to be modified.\n\
-c [num]                The channels index of the target param blob, \
if not set, all channels will be set.'

    try:
        opts, args = getopt.getopt(argv, 'hp:o:m:v:c:')
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt == '-p':
            proto_file = arg
        elif opt == '-o':
            out_file = arg
        elif opt == '-m':
            caffemodel_file = arg
        elif opt == '-v':
            param_name = arg
        elif opt == '-c':
            channel_idx = int(arg)

    if proto_file is None or out_file is None:
        print help_msg
        sys.exit()

    # Load the caffe
    I('Loading the %s' % proto_file)
    if caffemodel_file is not None:
        net = caffe.Net(proto_file, caffemodel_file, caffe.TEST)
    else:
        net = caffe.Net(proto_file, caffe.TEST)

    param_list = net.params.keys()
    # If the param_name is not set, ask for it
    while param_name is None or param_name not in param_list:
        I('Net params:')
        for blob in param_list:
            print('%s %s' % (blob, str(net.params[blob][0].data.shape)))
        param_name = raw_input('Input the blob name: ')

    ksize = net.params[param_name][0].data.shape[2:]
    I('The size of kernel %s is %s' % (param_name, str(ksize)))
    # make Gaussian blur
    sigma = 1.
    y, x = np.mgrid[-ksize[0]//2 + 1:ksize[0]//2 + 1,
                    -ksize[1]//2 + 1:ksize[1]//2 + 1]
    g = np.exp(-((x**2 + y**2)/(2.0*sigma**2)))
    gaussian = (g / g.sum()).astype(np.float32)
    I('The kernel is:')
    print(str(gaussian))
    if channel_idx is None:
        net.params[param_name][0].data[:, :, ...] = gaussian
    else:
        net.params[param_name][0].data[:, :, channel_idx, ...] = gaussian
    # Save the model
    I('Saving the model to %s' % out_file)
    net.save(out_file)


if __name__ == '__main__':
    main(sys.argv[1:])

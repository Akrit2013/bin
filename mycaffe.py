#!/usr/bin/python

# This is a wrapper of the caffe tools
# 1. The additional warning or error log will be disabled
# 2. The log file will be saved in the ./log path instead of /tmp
# 3. The train curve will be plot and saved in the ./log/fig

import glog as log
import time_tools
import timer_lib
import path_tools
import sys
import os
import tools
import shutil
import imshow_lib
import time
import threading
import random
import crash_on_ipy


def disp_thread(cmd_list, flag):
    # Define the refresh interval
    DEF_REFRESH_TIME = 300
    CURR_REFRESH_TIME = DEF_REFRESH_TIME
    # Define the sleep time
    DEF_SLEEP_TIME = 5
    ish = imshow_lib.Imshow()
    # Show the figure
    ish.show()
    timer = timer_lib.timer(start=True)
    im_path = cmd_list[2]

    while flag[0]:
        # Check if need to refresh
        if timer.elapse() > CURR_REFRESH_TIME:
            # Add random time to avoid the conflict between different instances
            CURR_REFRESH_TIME = DEF_REFRESH_TIME + random.randint(-100, 100)
            try:
                # When test iter is 0, there will be an error since
                # no test data
                os.system(list2str(cmd_list))
            except:
                # Only disp the train loss curve
                cmd_list[1] = '6'
                try:
                    os.system(list2str(cmd_list))
                except:
                    log.error('\033[01;31mERROR:\033[0m Can not generate \
the figure')
            # Show the image
            try:
                ish.imshow(im_path)
            except:
                log.error('\033[01;31mERROR:\033[0m Can not display the image')
            timer.start()
        time.sleep(DEF_SLEEP_TIME)


def parse_argv(lst):
    """
    Parse the argv param to get the info
    If in train process, prepare to store the log
    It in test process, return None
    The return is a string cotains the solver name and
    the current time, such as:
        solver_ex1.2_0301.0232.32
    """
    if lst[0] != 'train':
        return None
    # Find the solver name
    solver = None
    for idx in range(len(lst)):
        item = lst[idx]
        if item == '-solver':
            solver = lst[idx+1]
            break
    else:
        log.warn('\033[0;32mWARNING\033[0m: Can not parse the solver name')
        return None
    # Formulate the return string
    # Get the time string
    time_str = time_tools.get_time_str()
    solver_str = path_tools.get_pure_name(solver)
    return solver_str + '_' + time_str


def list2str(lst):
    """
    This function convert the list to string
    """
    rst_str = ''
    for item in lst:
        rst_str = rst_str + ' ' + str(item)
    return rst_str


def main(argv):
    # Start the timer
    timer = timer_lib.timer(True)

    log_path = './log'
    tmp_path = '/tmp'

    cmd = 'plot_log.py'
    # This is used when the main plot script crashed
    plt_cmd = 'plot_parsed_log.py'

    log_name = 'caffe.INFO'

    help_msg = 'This script take the same cammand parameters as \
the caffe does\n\
--disp      Try to display the loss curve while training.\n\
--no-test   Set it if the solver contains no test.'

    is_disp = False
    is_no_test = False
    disp_hThread = None
    disp_signal = [True]

    if '--disp' in argv:
        is_disp = True
        argv.remove('--disp')
    if '--no-test' in argv:
        is_no_test = True
        argv.remove('--no-test')

    if len(argv) == 0:
        print help_msg
        sys.exit()

    # Parse the params first to get the information
    path_name = parse_argv(argv)
    if path_name is not None:
        raw_path = path_tools.get_full_path(tmp_path, path_name)
        log.info('The raw log will be saved in \033[0;32m%s\033[0m'
                 % raw_path)
        local_path = path_tools.get_full_path(log_path, path_name)
        log.info('The local log will be saved in \033[0;32m%s\033[0m'
                 % local_path)
        # Check the path
        path_tools.check_path(log_path)
        path_tools.check_path(raw_path)
        path_tools.check_path(local_path)

        # Change the path to store the log files
        os.environ['GLOG_log_dir'] = raw_path
        # Only keep the INFO
        os.environ['GLOG_logtostderr'] = '0'

    # Generate the readable log file
    raw_log = path_tools.get_full_path(raw_path, log_name)
    if is_no_test:
        cmd_p1 = '6'
    else:
        cmd_p1 = '60'
    cmd_p2 = path_tools.get_full_path(local_path, 'fig.png')
    cmd_p3 = raw_log
    cmd_list = [cmd, cmd_p1, cmd_p2, cmd_p3]

    if is_disp:
        log.info('\033[01;32mStart thread to draw the loss curve\033[0m')
        disp_hThread = threading.Thread(
            target=disp_thread,
            args=(cmd_list, disp_signal)
        )
        disp_hThread.start()

    # The main training process
    os.system(list2str(['caffe']+argv))

    # Wait the disp thread exit if needed
    if is_disp:
        log.info('Waiting for the disp thread exist')
        disp_signal[0] = False
        disp_hThread.join()

    # After the training
    # Generate the readable log file
    raw_log = path_tools.get_full_path(raw_path, log_name)
    if is_no_test:
        cmd_p1 = '6'
    else:
        cmd_p1 = '60'
    cmd_p2 = path_tools.get_full_path(local_path, 'fig.png')
    cmd_p3 = raw_log
    cmd_list = [cmd, cmd_p1, cmd_p2, cmd_p3]
    # plot the log curve and save it to local_path
    try:
        os.system(list2str(cmd_list))
    except:
        log.error('\033[31mERROR\033[0m: Can not plot using plot_log.py, \
trying the backup option')
        cmd1 = path_tools.get_full_path(local_path, 'caffe.INFO.train')
        plt_cmd_list = [plt_cmd, '-i', cmd1, '-o', cmd_p2]
        os.system(list2str(plt_cmd_list))
    timer.stop()
    log.info('The figure and log data are saved in \033[01;31m%s\033[0m'
             % local_path)
    log.info('Training Time: \033[01;32m%s\033[0m' % timer.to_str())
    log.info('Should the LOG file be kept? \033[0;33m[Y/n]\033[0m')
    os.system('%s %s' % ('xdg-open', cmd_p2))
    ch = tools.get_char()
    if ch == 'n' or ch == 'N':
        log.info('\033[01;31mDeleting the log files ...\033[0m')
        shutil.rmtree(local_path)
        shutil.rmtree(raw_path)
        log.info('Finish.')
    else:
        log.info('Keep the log files')


if __name__ == '__main__':
    main(sys.argv[1:])

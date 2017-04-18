#!/usr/bin/python

# This is a script can kill the process by the process name
# It will list a couple of processes contains the target name
# and the user can kill one of them according to the index
# Usage:
#   kill.py process_name
# Version 1.1

import os
import sys
import tabulate
import psutil
import time
import color_lib
import time_tools
import crash_on_ipy


def list2str(lst):
    """
    Convert the list to string
    """
    rst = ''
    for ele in lst:
        rst = rst + str(ele) + ' '
    return rst[:-1]


def match_keywords(keyword_list1, keyword_list2):
    """
    This function will return True if all keywords in keyword_list2
    can be found in keyword_list1
    """
    if len(keyword_list2) == 0:
        return True
    for key2 in keyword_list2:
        for key1 in keyword_list1:
            if key2.lower() in key1.lower():
                break
        else:
            return False
    return True


def main(argv):
    # If the cpu percent larget than the val, highlight it
    DEF_CPU_THD1 = 10
    DEF_CPU_THD2 = 100
    DEF_CPU_THD3 = 1000
    # Define the mem percentage thd
    DEF_MEM_THD1 = 1.0
    DEF_MEM_THD2 = 10
    # If the start time of the thread small than the thd, highlight it
    # in seconds
    DEF_TIME_THD1 = 60
    DEF_TIME_THD2 = 600
    # Define the max length of the cmdline
    DEF_CMDLINE_LEN = 100
    # Define the max length of name
    DEF_NAME_LEN = 50

    if len(argv) == 0:
        print 'Usage: kill.py thread_keyword1 [thread_keyword2]'
        print 'list all process:'

    curr_user = None
    self_pid = os.getpid()

    keyword_list = argv
    # Get all the thread IDs
    pid_list = psutil.pids()

    # Loop each id to find the right threads
    thread_list = []
    for pid in pid_list:

        if pid == self_pid:
            p = psutil.Process(pid)
            curr_user = p.username()
            continue

        # Incase some process existed
        try:
            p = psutil.Process(pid)
        except:
            continue
        name = p.name()
        cmdline_list = p.cmdline()
        if len(cmdline_list) == 0:
            cmdline = ['N/A']
        else:
            cmdline = cmdline_list
        p_keyword_list = name.split() + cmdline
        # Find if the thread match the keyword_list
        if match_keywords(p_keyword_list, keyword_list):
            thread_list.append(p)
            continue

    color = color_lib.color()
    # Display the Process list (except the kill.sh)
    # Define the head of the table
    head = ['ID', 'Pid', 'Name', 'Cmdline', 'Time', 'CPU', 'MEM']
    table = []

    for idx in range(len(thread_list)):
        p = thread_list[idx]
        ID = idx + 1

        user = p.username()
        if user == 'root':
            ID = color.set_color(ID, 'red')
        elif user == curr_user:
            ID = color.set_color(ID, 'green')
        else:
            ID = color.set_color(ID, 'yellow')

        name = p.name()
        # Restrict the length of name section
        if len(name) > DEF_NAME_LEN:
            name = name[:DEF_NAME_LEN]
        # If the name include the keyword, highlight the name
        if match_keywords(name.split(), keyword_list):
            name = color.set_color(name, 'green')

        cmdline_list = p.cmdline()
        if len(cmdline_list) == 0:
            cmdline = 'N/A'
        else:
            cmdline = list2str(cmdline_list)

        # Makesure the cmdline is not too long
        if len(cmdline) > DEF_CMDLINE_LEN:
            cmdline = cmdline[:DEF_CMDLINE_LEN]
        # If cmdline include the keyword, highlight it
        if match_keywords([cmdline], keyword_list):
            cmdline = color.set_color(cmdline, 'green')

        cpu_times = p.cpu_times()
        cpu = cpu_times.user + cpu_times.system
        if cpu > DEF_CPU_THD3:
            cpu = color.set_color(cpu, 'red')
        elif cpu > DEF_CPU_THD2:
            cpu = color.set_color(cpu, 'yellow')
        elif cpu > DEF_CPU_THD1:
            cpu = color.set_color(cpu, 'green')
        else:
            cpu = str(cpu)

        mem = p.memory_percent()
        if mem > DEF_MEM_THD2:
            mem = color.set_color(mem, 'red')
        elif mem > DEF_MEM_THD1:
            mem = color.set_color(mem, 'yellow')
        else:
            mem = str(mem)

        run_time = time.time() - p.create_time()
        run_time_str = time_tools.sec2time(run_time)
        if run_time < DEF_TIME_THD1:
            cmdline = color.set_color(cmdline, 'green')
            run_time_str = color.set_color(run_time_str, 'green')
        elif run_time < DEF_TIME_THD2:
            cmdline = color.set_color(cmdline, 'yellow')
            run_time_str = color.set_color(run_time_str, 'yellow')

        pid = p.pid
        if pid < 1000:
            pid = color.set_color(pid, 'red')
        else:
            pid = str(pid)

        # If the cmdline contains chinese, it should be decoded to utf8 before
        # show in tabulate
        try:
            cmdline = cmdline.decode()
        except:
            cmdline = cmdline.decode('utf8')
        # Combine the list
        line = [ID, pid, name, cmdline, run_time_str, cpu, mem]
        table.append(line)
    # Print the table
    print tabulate.tabulate(table, headers=head)

    if len(table) == 0:
        sys.exit()
    # Kill the target process
    ID = raw_input('Input the \033[01;31mID\033[0m of process \
to \033[01;31mKILL\033[0m: ')
    try:
        ID = int(ID)
        p = thread_list[ID-1]
    except:
        print color.set_color('Invaild INPUT, exist the script.', 'yellow')
        sys.exit()

    # Kill
    cmdline = list2str(p.cmdline())
    if len(cmdline) == 0:
        cmdline = 'N/A'
    print 'Kill the ' + color.set_color(cmdline, 'red')
    p.kill()


if __name__ == '__main__':
    main(sys.argv[1:])

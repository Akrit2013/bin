#!/usr/bin/python

# Version: 0.8.1
# This script encode the video using the x265/x264 encoder and merge the
# encoded video with subtitles into a mkv file

import getopt
import subtitle_tools
import sys
import os
import log_tools
import time_tools
import ConfigParser
import video_tools
import common_tools
import tabulate
import color_lib


def preprocess_str(in_str):
    """
    This function preprocess the input file name
    and \ in front of the space and &
    """
    in_str = in_str.replace('&', '\&')
    in_str = in_str.replace(' ', '\ ')
    in_str = in_str.replace('(', '\(')
    in_str = in_str.replace(')', '\)')
    in_str = in_str.replace("'", "\\'")
    return in_str


def fit_resolution(length, unit):
    """
    Fit the resolution to the nearest unit resolution
    """
    w_mod = length % unit
    if w_mod < unit / 2:
        new_length = length - w_mod
    else:
        new_length = length + unit - w_mod
    return new_length


def find_best_resolution(src_width, src_height, zoom, unit,
                         search_range=0.05, search_step=0.01):
    """
    This function find the best resolution with the lowest error
    according to the given width and height
    """
    lowest_err = float('inf')
    target_width = None
    target_height = None
    # Generate the search zoom list
    for val in common_tools.frange(zoom-search_range,
                                   zoom+search_range,
                                   search_step):
        # Get the target resolution according to zoom rate
        height = round(val * float(src_height))
        width = round(val * float(src_width))
        # Get the fitted resolution
        height_fit = fit_resolution(height, unit)
        width_fit = fit_resolution(width, unit)
        # Calc the error according to the unit
        h_err = abs(height - height_fit)
        w_err = abs(width - width_fit)
        err = h_err + w_err
        if err < lowest_err:
            target_width = width_fit
            target_height = height_fit
            lowest_err = err
    return [target_width, target_height, lowest_err]


def interactive(rst_dict):
    """
    This function use the interactive mode to get the param
    only if the param is None, the param will be set
    """
    color = color_lib.color()
    if 'vencoder' not in rst_dict or rst_dict['vencoder'] is None:
        log_tools.log_info('Select the \033[01;33mvideo encoder\033[0m:')
        tab = tabulate.tabulate([['0.copy',
                                  color.set_color('1.libx265', 'green'),
                                  '2.libx264']])
        print(tab)
        ch = raw_input('input:')
        try:
            select = int(ch)
        except:
            select = -1

        if select == 0:
            rst_dict['vencoder'] = 'copy'
        elif select == 1:
            rst_dict['vencoder'] = 'libx265'
        elif select == 2:
            rst_dict['vencoder'] = 'libx264'
        else:
            rst_dict['vencoder'] = 'libx265'

        log_tools.log_info('Use video encoder \033[01;31m%s\033[0m'
                           % rst_dict['vencoder'])

    if 'vpreset' not in rst_dict or rst_dict['vpreset'] is None:
        rst_dict['vpreset'] = 'veryslow'
        log_tools.log_info('Select the video \033[01;33mencoding \
preset\033[0m:')
        tab = tabulate.tabulate([['1.ultrafast', '2.superfast',
                                  '3.veryfast', '4.faster', '5.medium',
                                  color.set_color('6.slow', 'green'),
                                  '7.slower', '8.veryslow', '9.placebo']])
        print(tab)
        ch = raw_input('input:')
        try:
            select = int(ch)
        except:
            select = -1

        if select == 1:
            rst_dict['vpreset'] = 'ultrafast'
        elif select == 2:
            rst_dict['vpreset'] = 'superfast'
        elif select == 3:
            rst_dict['vpreset'] = 'veryfast'
        elif select == 4:
            rst_dict['vpreset'] = 'faster'
        elif select == 5:
            rst_dict['vpreset'] = 'medium'
        elif select == 6:
            rst_dict['vpreset'] = 'slow'
        elif select == 7:
            rst_dict['vpreset'] = 'slower'
        elif select == 8:
            rst_dict['vpreset'] = 'veryslow'
        elif select == 9:
            rst_dict['vpreset'] = 'placebo'
        else:
            rst_dict['vpreset'] = 'slow'

        log_tools.log_info('Use video preset \033[01;31m%s\033[0m'
                           % rst_dict['vpreset'])

    if 'vcrf' not in rst_dict or rst_dict['vcrf'] is None:
        log_tools.log_info('Input the \033[01;33mCRF\033[0m value \
[default = 23]')
        ch = raw_input('input:')
        try:
            select = int(ch)
        except:
            select = 23
        rst_dict['vcrf'] = select
        log_tools.log_info('Use video crf \033[01;31m%d\033[0m'
                           % rst_dict['vcrf'])

    if 'vzoom' not in rst_dict or rst_dict['vzoom'] is None:
        log_tools.log_info('Input the \033[01;33mzoom\033[0m value \
[default = 1.0]')
        ch = raw_input('input:')
        try:
            select = float(ch)
        except:
            select = 1.0
        rst_dict['vzoom'] = select

        log_tools.log_info('Use video zoom \033[01;31m%f\033[0m'
                           % rst_dict['vzoom'])

    if ('vunit' not in rst_dict or rst_dict['vunit'] is None)\
            and rst_dict['vzoom'] != 1:
        log_tools.log_info('Select the basic block \033[01;33munit\033[0m \
for resize:')
        tab = tabulate.tabulate([[color.set_color('1.16x16', 'green'),
                                  '2.32x32']])
        print(tab)
        ch = raw_input('input:')
        try:
            select = int(ch)
        except:
            select = -1
        if select == 1:
            rst_dict['vunit'] = 16
        elif select == 2:
            rst_dict['vunit'] = 32
        else:
            rst_dict['vunit'] = 16

        log_tools.log_info('Use video unit \033[01;31m%d\033[0m'
                           % rst_dict['vunit'])
    else:
        # If not zoon, the vunit param is not used
        rst_dict['vunit'] = 16

    if 'aencoder' not in rst_dict or rst_dict['aencoder'] is None:
        log_tools.log_info('Select the \033[01;33mAudio encoder\033[0m:')
        tab = tabulate.tabulate([['0.copy',
                                  color.set_color('1.libfdk_aac', 'green')]])
        print(tab)
        ch = raw_input('input:')
        try:
            select = int(ch)
        except:
            select = -1
        if select == 0:
            rst_dict['aencoder'] = 'copy'
            # Set the abr for compitable
            rst_dict['abr'] = '384k'
        elif select == 1:
            rst_dict['aencoder'] = 'libfdk_aac'
        else:
            rst_dict['aencoder'] = 'libfdk_aac'

        log_tools.log_info('Use Audio encoder \
\033[01;31m%s\033[0m' % rst_dict['aencoder'])

    if 'abr' not in rst_dict or rst_dict['abr'] is None:
        log_tools.log_info('Select the \033[01;33maudio bit rate\033[0m:')
        tab = tabulate.tabulate([[color.set_color('1.384k', 'green'),
                                  '2.192k', '3.128k', '4.64k']])
        print(tab)
        ch = raw_input('input:')
        try:
            select = int(ch)
        except:
            select = -1

        if select == 1:
            rst_dict['abr'] = '384k'
        elif select == 2:
            rst_dict['abr'] = '192k'
        elif select == 3:
            rst_dict['abr'] = '128k'
        elif select == 4:
            rst_dict['abr'] = '64k'
        else:
            rst_dict['abr'] = '384k'

        log_tools.log_info('Use audio bitrate \033[01;31m%s\033[0m'
                           % rst_dict['abr'])
    return rst_dict


def get_language(subtitle):
    track_name = None
    if subtitle is not None:
        # Guess the language
        lang = subtitle_tools.guess_language(subtitle)
        track_name = subtitle_tools.guess_track_name(subtitle)
        if lang is None:
            lang = subtitle_tools.detect_language(subtitle)

        if lang is not None:
            log_tools.log_info('Lanauge of %s is \033[01;32m%s\033[0m'
                               % (subtitle, lang))
        else:
            # und indicate undetermined language in mkvmerge
            lang = 'und'
            log_tools.log_warn('Can not determine the language of %s'
                               % subtitle)

        if track_name is not None:
            log_tools.log_info('Track name of %s is \033[01;32m%s\033[0m'
                               % (subtitle, track_name))
        else:
            log_tools.log_warn('Can not determine the track name of %s'
                               % subtitle)

    else:
        lang = None
    return (lang, track_name)


def default_setting(rst_dict):
    """
    Check the encode setting, if None found, set the default value
    """
    if 'vencoder' not in rst_dict or rst_dict['vencoder'] is None:
        rst_dict['vencoder'] = 'libx265'
        log_tools.log_info('Use default video encoder \033[01;31m%s\033[0m'
                           % rst_dict['vencoder'])

    if 'vpreset' not in rst_dict or rst_dict['vpreset'] is None:
        rst_dict['vpreset'] = 'slow'
        log_tools.log_info('Use default video preset \033[01;31m%s\033[0m'
                           % rst_dict['vpreset'])

    if 'vcrf' not in rst_dict or rst_dict['vcrf'] is None:
        rst_dict['vcrf'] = 23
        log_tools.log_info('Use default video crf \033[01;31m%d\033[0m'
                           % rst_dict['vcrf'])

    if 'vzoom' not in rst_dict or rst_dict['vzoom'] is None:
        rst_dict['vzoom'] = 1.0
        log_tools.log_info('Use default video zoom \033[01;31m%f\033[0m'
                           % rst_dict['vzoom'])

    if 'vunit' not in rst_dict or rst_dict['vunit'] is None:
        rst_dict['vunit'] = 16
        log_tools.log_info('Use default video unit \033[01;31m%d\033[0m'
                           % rst_dict['vunit'])

    if 'aencoder' not in rst_dict or rst_dict['aencoder'] is None:
        rst_dict['aencoder'] = 'libfdk_aac'
        log_tools.log_info('Use default audio encoder \033[01;31m%s\033[0m'
                           % rst_dict['aencoder'])

    if 'abr' not in rst_dict or rst_dict['abr'] is None:
        rst_dict['abr'] = '384k'
        log_tools.log_info('Use default audio bitrate \033[01;31m%s\033[0m'
                           % rst_dict['abr'])
    return rst_dict


def parse_conf(config_file):
    """
    Parse the config file and return a dict contains the parameter set
    """
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    MAIN_SEC = 'video'
    SUB_SEC = 'encoder'
    try:
        vencoder = config.get(MAIN_SEC, SUB_SEC)
        log_tools.log_info('Encoder: \033[01;32m%s\033[0m' % vencoder)
    except:
        vencoder = None
        log_tools.log_warn('Can not find %s %s, use \
default \033[01;32m%s\033[0m' % (MAIN_SEC, SUB_SEC, vencoder))

    SUB_SEC = 'preset'
    try:
        vpreset = config.get(MAIN_SEC, SUB_SEC)
        log_tools.log_info('Video Preset: \033[01;32m%s\033[0m' % vpreset)
    except:
        vpreset = None
        log_tools.log_warn('Can not find %s %s, use \
default \033[01;32m%s\033[0m' % (MAIN_SEC, SUB_SEC, vpreset))

    SUB_SEC = 'crf'
    try:
        crf = config.getint(MAIN_SEC, SUB_SEC)
        log_tools.log_info('Video crf: \033[01;32m%d\033[0m' % crf)
    except:
        crf = None
        log_tools.log_warn('Can not find %s %s, use \
default \033[01;32m%d\033[0m' % (MAIN_SEC, SUB_SEC, crf))

    SUB_SEC = 'zoom'
    try:
        zoom = config.getfloat(MAIN_SEC, SUB_SEC)
        log_tools.log_info('Video zoom: \033[01;32m%f\033[0m' % zoom)
    except:
        zoom = None
        log_tools.log_warn('Can not find %s %s, use \
default \033[01;32m%f\033[0m' % (MAIN_SEC, SUB_SEC, zoom))

    SUB_SEC = 'unit'
    try:
        unit = config.getint(MAIN_SEC, SUB_SEC)
        log_tools.log_info('Video unit: \033[01;32m%d\033[0m' % unit)
    except:
        unit = None
        log_tools.log_warn('Can not find %s %s, use \
default \033[01;32m%d\033[0m' % (MAIN_SEC, SUB_SEC, unit))

    MAIN_SEC = 'audio'
    SUB_SEC = 'encoder'
    try:
        aencoder = config.get(MAIN_SEC, SUB_SEC)
        log_tools.log_info('Audio encoder: \033[01;32m%s\033[0m' % aencoder)
    except:
        aencoder = None
        log_tools.log_warn('Can not find %s %s, use \
default \033[01;32m%s\033[0m' % (MAIN_SEC, SUB_SEC, aencoder))

    SUB_SEC = 'br'
    try:
        br = config.get(MAIN_SEC, SUB_SEC)
        log_tools.log_info('Audio bitrate: \033[01;32m%s\033[0m' % br)
    except:
        br = None
        log_tools.log_warn('Can not find %s %s, use \
default \033[01;32m%s\033[0m' % (MAIN_SEC, SUB_SEC, br))

    rst_dict = {}
    rst_dict['vencoder'] = vencoder
    rst_dict['vpreset'] = vpreset
    rst_dict['vcrf'] = crf
    rst_dict['vzoom'] = zoom
    rst_dict['vunit'] = unit
    rst_dict['aencoder'] = aencoder
    rst_dict['abr'] = br
    return rst_dict


def main(argv):
    config_file = None
    in_video = None
    out_video = None
    s1_file = None
    s2_file = None
    s3_file = None
    s4_file = None
    param_dict = {}

    has_subtitle = False
    has_verbose = False
    is_interactive = False

    color = color_lib.color(True)

    help_msg = 'video_encode -i <video> -o <video.mkv> -c [config] \
--s1 [subtitle]\n\
-i <video>      The input video to be encoded\n\
-o <video.mkv>  The output edefault ncoded video\n\
-c [config]     The config file including resolution, V/A code rate\n\
--s1 [subtitle] The subtitle to be merged\n\
--s2 [subtitle] The second subtitle to be merged\n\
--s3 [subtitle] The third subtitle to be merged\n\
--s4 [subtitle] The forth subtitle to be merged\n\
-a              If set, use interactive mode to set the params\n\
-v              Enable the verbose output of ffmpeg.'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:c:av', ['s1=',
                                                       's2=',
                                                       's3=',
                                                       's4='])
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt == '-i':
            in_video = preprocess_str(arg)
        elif opt == '-o':
            out_video = preprocess_str(arg)
        elif opt == '-c':
            config_file = preprocess_str(arg)
        elif opt == '-a':
            is_interactive = True
        elif opt == '--s1':
            s1_file = preprocess_str(arg)
            has_subtitle = True
        elif opt == '--s2':
            s2_file = preprocess_str(arg)
            has_subtitle = True
        elif opt == '--s3':
            s3_file = preprocess_str(arg)
            has_subtitle = True
        elif opt == '--s4':
            s4_file = preprocess_str(arg)
            has_subtitle = True
        elif opt == '-v':
            has_verbose = True

    if in_video is None or out_video is None:
        print help_msg
        sys.exit()

    # The step1 out name
    # If no subtitle assigned, ffmpeg directly output the result
    if has_subtitle:
        step1_file = 'tmp' + time_tools.get_time_str() + '.mkv'
    else:
        step1_file = out_video

    # Display the video basic info
    video_tools.print_video_basic_info(in_video)

    # Load the config file
    if config_file is None:
        log_tools.log_info('Config file is not set, use the default setting')
    else:
        param_dict = parse_conf(config_file)

    if is_interactive:
        # Use interactive mode to set the param
        param_dict = interactive(param_dict)
    else:
        # Set the default param
        param_dict = default_setting(param_dict)

    # If need to resize the video, find the best resize resolution according to
    # the zoom rate and the basic coding unit size
    if param_dict['vzoom'] is not None and param_dict['vzoom'] != 1:
        # Get the orginal resolution of the video
        [org_width, org_height] = video_tools.get_video_resolution(in_video)
        log_tools.log_info('The orginal video resolution is \
\033[0;32m%dx%d\033[0m' % (org_width, org_height))
        [zoom_width, zoom_height, err] = \
            find_best_resolution(org_width,
                                 org_height,
                                 param_dict['vzoom'],
                                 param_dict['vunit'])

        log_tools.log_info('The resized video resolution is \
\033[0;32m%dx%d\033[0m, err: \033[0;31m%d\033[0m'
                           % (zoom_width, zoom_height, err))

        # the commond line for the ffmpeg with resize video
        cmd_str_ffmpeg = 'ffmpeg -i %s -c:v %s -preset %s -crf %d -c:a %s \
-b:a %s -s %dx%d' % (in_video, param_dict['vencoder'],
                     param_dict['vpreset'], param_dict['vcrf'],
                     param_dict['aencoder'], param_dict['abr'],
                     zoom_width, zoom_height)
    else:
        # the commond line for the ffmpeg without resize video
        cmd_str_ffmpeg = 'ffmpeg -i %s -c:v %s -preset %s -crf %d -c:a %s \
-b:a %s' % (in_video, param_dict['vencoder'], param_dict['vpreset'],
            param_dict['vcrf'], param_dict['aencoder'],
            param_dict['abr'])

    # Disable the verbose output of ffmpeg
    if not has_verbose:
        cmd_str_ffmpeg = cmd_str_ffmpeg + ' -v 1'
    # Search larger range to void the missing subtitles (optional)
    cmd_str_ffmpeg = cmd_str_ffmpeg + ' -analyzeduration 1000000k \
-probesize 1000000k'
    # Ignore unknow stream type and print progress report
    cmd_str_ffmpeg = cmd_str_ffmpeg + ' -ignore_unknown -stats'
    # Copy the subtitles
    cmd_str_ffmpeg = cmd_str_ffmpeg + ' -c:s copy'
    # Add map command to make sure all tracks are converted
    cmd_str_ffmpeg = cmd_str_ffmpeg + ' -map 0'
    # Add the output
    cmd_str_ffmpeg = cmd_str_ffmpeg + ' ' + step1_file

    # Display the video length if can
    len_str = video_tools.get_video_length_str(in_video)
    if len_str is not None:
        len_str = color.red(len_str)
        log_tools.log_info('Start to encode %s / %s' % (len_str, in_video))
    else:
        log_tools.log_info('Start to encode %s' % in_video)

    # Display the cmd line
    log_tools.log_info('\033[0;33m%s\033[0m' % cmd_str_ffmpeg)
    # Start encode
    os.system(cmd_str_ffmpeg)
    log_tools.log_info('Encoding finished.')

    if not has_subtitle:
        log_tools.log_info('The encode output: \033[0;32m%s\033[0m'
                           % step1_file)
        sys.exit()

    log_tools.log_info('Merge subtitles into MKV file')
    log_tools.log_info('Guessing the language of the subtitle')
    lang1, track_name1 = get_language(s1_file)
    lang2, track_name2 = get_language(s2_file)
    lang3, track_name3 = get_language(s3_file)
    lang4, track_name4 = get_language(s4_file)

    # Generate the subtitle list
    sub_list = []
    lang_list = []
    track_name_list = []
    if s1_file is not None:
        sub_list.append(s1_file)
        lang_list.append(lang1)
        track_name_list.append(track_name1)
        # Try to convert the subtitle to UTF8
        enca_cmd = 'enca -L zh_CN -x UTF-8 %s' % s1_file
        os.system(enca_cmd)

    if s2_file is not None:
        sub_list.append(s2_file)
        lang_list.append(lang2)
        track_name_list.append(track_name2)
        # Try to convert the subtitle to UTF8
        enca_cmd = 'enca -L zh_CN -x UTF-8 %s' % s2_file
        os.system(enca_cmd)

    if s3_file is not None:
        sub_list.append(s3_file)
        lang_list.append(lang3)
        track_name_list.append(track_name3)
        # Try to convert the subtitle to UTF8
        enca_cmd = 'enca -L zh_CN -x UTF-8 %s' % s3_file
        os.system(enca_cmd)

    if s4_file is not None:
        sub_list.append(s4_file)
        lang_list.append(lang4)
        track_name_list.append(track_name4)
        # Try to convert the subtitle to UTF8
        enca_cmd = 'enca -L zh_CN -x UTF-8 %s' % s4_file
        os.system(enca_cmd)

    # Generate the merge cmd line
    mkv_cmd_list = 'mkvmerge -o %s --default-track 0' % out_video
    id_counter = 0
    for sub, lang, track_name in zip(sub_list, lang_list, track_name_list):
        mkv_cmd_list = mkv_cmd_list + ' --language %d:%s' % (id_counter,
                                                             lang)
        if track_name is not None:
            mkv_cmd_list = mkv_cmd_list + ' --track-name %d:%s' % (id_counter,
                                                                   track_name)
        mkv_cmd_list = mkv_cmd_list + ' %s' % sub
#        id_counter += 1

    mkv_cmd_list = mkv_cmd_list + ' ' + step1_file
    # Print the mkvmerge cmd
    log_tools.log_info('\033[0;33m%s\033[0m' % mkv_cmd_list)
    os.system(mkv_cmd_list)
    # Check the output video, and del the tmp file
    if os.path.isfile(out_video):
        os.remove(step1_file)
        log_tools.log_info('Finished. Output video \033[01;32m%s\033[0m'
                           % out_video)
    else:
        log_tools.log_err('Can not find the output video \033[01;31m%s\033[0m'
                          % out_video)
        log_tools.log_warn('Not delete the temporary \033[01;33m%s\033[0m'
                           % step1_file)


if __name__ == '__main__':
    main(sys.argv[1:])

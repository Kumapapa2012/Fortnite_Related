#
# this script supports binary from https://github.com/BtbN/FFmpeg-Builds/releases

import os
import subprocess
import re
import argparse 
import datetime as dt
import shutil
import configparser
import inspect

# コマンドライン処理
source_file_path = inspect.getfile(inspect.currentframe())
parser = argparse.ArgumentParser(
                    prog='Fortnite Hilight Video processor',
                    description='Concat Hilights videos produced by Geforce Experience',
                    epilog='{0} PATH_TO_DIR_WHICH_CONTAINS_ONLY_HILIGHTS_TO_PROCESS'.format(os.path.basename(source_file_path)))

parser.add_argument('dirname')   
args = parser.parse_args()

# 順序の処理
def ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return str(n) + suffix

# 環境の処理
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

pattern_str = config.get('File', 'pattern_Highlights')
pattern = re.compile(pattern_str)
print(pattern)

ffmpeg = config['Video_Process']['ffmpeg_path']
ffprobe = config['Video_Process']['ffprobe_path']
# fade in
ffmpeg_effect = ' '.join([ffmpeg, config['Video_Process']['cmd_effect']])
# add datetime
ffmpeg_text = ' '.join([ffmpeg, config['Video_Process']['cmd_text']])
# concat
ffmpeg_concat = ' '.join([ffmpeg, config['Video_Process']['cmd_concat']])
# schene detection
##ffmpeg_schene_detect = ' '.join([ffmpeg, config['Video_Process']['cmd_schene_detect']])

# Video Duration
ffprobe_video_duration = ' '.join([ffprobe, config['Video_Process']['cmd_duration_prove']])

# archive
archive_folder = config['File']['archive_folder']
os.makedirs(archive_folder, exist_ok=True)

# temp folder to work
os.makedirs("output", exist_ok=True)

# Highlights の取得
files = sorted(os.listdir(args.dirname))
table_Highlights=[]
filename_tmp="Fortnite-Kills - {0}"


## START!!!

# Check filename timegap so to avoid duplicated scenes.
prev_hilight_datetime = dt.datetime(1970, 1, 1)
SAME_VIDEO_THRESHOLD=13

for file in files:
    if not re.match(pattern, os.path.basename(file)):
        print("ファイル名は指定されたパターンにマッチしません。: {0}".format(file))
        continue

    # Large files are skipped
    if os.path.getsize(args.dirname+"\\"+file) > 200000000: # > 200MB
        print("ファイル名はインスタントリプレイの物と見られます。: {0}".format(file))
        continue

    file_name=os.path.basename(file)

    #   extract date and timestamp
    #   create text to be rendered on the video
    date_matches = re.findall(pattern, file_name)

    date_format = "%Y.%m.%d - %H.%M.%S.%f"
    date_object = dt.datetime.strptime(date_matches[0][0], date_format)
    label_text = date_object.strftime("%Y/%m/%d-%X")

    if prev_hilight_datetime and date_object - prev_hilight_datetime > dt.timedelta(seconds=SAME_VIDEO_THRESHOLD):
        table_Highlights.append((file_name,label_text))
        prev_hilight_datetime = date_object
    else:
        #replace the last one to current one
        table_Highlights.append((file_name,label_text))  if len(table_Highlights) == 0 else table_Highlights.__setitem__(-1, (file_name,label_text))
        #and keeps prev_hilight_datetime

for entry in table_Highlights:
    
    # Phase 1 - Fade-in

    cmd1 = ffmpeg_effect.format( args.dirname+'\\'+entry[0])
    print("!! Running " +cmd1)
    os.system(cmd1)
    
    # Phase 2 - Timestamp in video
    
    # https://stackoverflow.com/questions/54046060/how-to-drawtext-colon-with-localtime-in-ffmpeg-filter-complex
    # due to difficulty of using ":" in drawtext, using textfile option
    with open("label.txt", "w") as file:
        file.write(entry[1])
    # cmd2 = cmdtmp2.format(args.dirname+'\\'+'processed_'+entry[0])
    cmd2 = ffmpeg_text.format('processed_' + entry[0])
    print("!! Running " +cmd2)
    os.system(cmd2)

########################
# Concatinate all
########################
pattern_processed = re.compile("processed_"+pattern_str)

## files_processed = sorted(os.listdir(args.dirname))
files_processed = sorted(os.listdir('.'))
table_Processed = []

for file in files_processed:
    if not re.match(pattern_processed, os.path.basename(file)):
        print("ファイル名は指定されたパターンにマッチしません。: {0}".format(file))
        continue
    #table.append(args.dirname + '\\' + file)
    table_Processed.append(file)
# Phase 1 - create a file list
with open("concat_flist.txt", "w") as file:
    for entry in table_Processed:   
        strtmp="file '{0}'".format(entry)+'\n'
        strtmp=strtmp.replace("\\","\\\\") 
        file.write(strtmp)

# Phase 2 - concat videos
cmd3=ffmpeg_concat
print(cmd3)
os.system(cmd3)


########################
# Wrap up
########################



# Phase 3 - scene detection
'''
cmd4=ffmpeg_schene_detect
print(cmd4)
os.system(cmd4)

pts_times=[]
with open("ffout.txt", "r") as file:
    pattern_pts = "pts_time:[0-9.]+"
    # pts_time:20.071029
    for line in file:
        # 行を処理（改行文字を削除して表示）
        if re.search(pattern_pts, line):
            pts_times.append(re.findall(pattern_pts, line)[0])
'''

# Phase 3 - Collect durations
pts_times = []
for entry in table_Processed:   
    cmd4=ffprobe_video_duration + ' "' + entry + '"'
    result = subprocess.check_output(cmd4,shell=True).decode().strip()
    pts_times.append(float(result))

#!!!!!
#exit(0)

scenes = [('0:00:00')]
ofs=0
for pts_time in pts_times:
    # seconds=float(pts_time.replace('pts_time:',''))
    seconds = pts_time
    ofs+=round(seconds)
    timestamp=dt.timedelta(seconds=ofs)
    scenes.append(str(timestamp))
# Remove the last one
del scenes[-1]

# wrap up
dst_fname = filename_tmp.format(dt.datetime.now().strftime("%c"))
dst_fname = dst_fname.replace(":","_").replace(" ","_").replace("/","_")

# Print Comment
strchapters=""
for index,scene in enumerate(scenes):
    strchapters=strchapters+f"{scene} - {ordinal(index+1)}"+'\n'

# copy video file 
print("copying video file...")
shutil.copy2("output_concat.mp4",args.dirname+"\\"+dst_fname+".mp4")

# create comment file
print("creating video comment...")
comment_v=''
with open('fortnite_kills_comment_template.txt', "r") as file_c1:
    comment_v = file_c1.read()
    comment_v=comment_v.format(strchapters)
    with open(args.dirname+'\\'+dst_fname+".txt", "w") as file_c2:
        file_c2.write(comment_v)

# clean up 
print("cleaning up...") 
print("moving processed videos to archive...")
for to_move in table_Processed:
    print("moving {0} to {1}".format(to_move,archive_folder))
    precheck_file = archive_folder+os.sep+to_move
    if(os.path.isfile(precheck_file)):
        os.remove(precheck_file)
    shutil.move(to_move, archive_folder)
print("deleting temp files...")
os.remove("output.mp4")
os.remove("output_concat.mp4")
os.remove("label.txt")
os.remove("concat_flist.txt")
#os.remove("ffout.txt")

print("Done!!!!!")
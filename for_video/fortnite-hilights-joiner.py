#
# this script supports binary from https://github.com/BtbN/FFmpeg-Builds/releases

import os
import re
import argparse 
import datetime as dt


def ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return str(n) + suffix


parser = argparse.ArgumentParser(
                    prog='Fortnite Hilight Video processor',
                    description='What the program does',
                    epilog='Text at the bottom of help')
parser.add_argument('dirname')   
args = parser.parse_args()

pattern_processed = r'processed_Fortnite (\d{4}\.\d{2}\.\d{2} - \d{2}\.\d{2}\.\d{2}\.\d{2})(\..+)?\.DVR\.mp4'

## files_processed = sorted(os.listdir(args.dirname))
files_processed = sorted(os.listdir('.'))
table=[]

cmdtmp3="ffmpeg -safe 0 -f concat -i test_flist.txt -c copy -y output_concate_test.mp4"
cmdtmp4="ffmpeg -i output_concate_test.mp4 -vf  \"select=gt(scene\,0.3), scale=640:360,showinfo\" -vsync vfr output/%04d.jpg -f null - 2> ffout.txt"
filename_tmp="Fortnite-Victory-Royale-{0}-Kills.mp4"

for file in files_processed:
    if not re.match(pattern_processed, os.path.basename(file)):
        print("ファイル名は指定されたパターンにマッチしません。: {0}".format(file))
        continue
    #table.append(args.dirname + '\\' + file)
    table.append(file)

# Phase 1 - create a file list
with open("test_flist.txt", "w") as file:
    for entry in table:   
        strtmp="file '{0}'".format(entry)+'\n'
        strtmp=strtmp.replace("\\","\\\\") 
        file.write(strtmp)

# Phase 2 - create a concat video
cmd1=cmdtmp3
#print(cmd1)
os.system(cmd1)

# Phase 3 - scene detection
cmd2=cmdtmp4
print(cmd1)
os.system(cmd2)

pts_times=[]
with open("ffout.txt", "r") as file:
    pattern_pts = "pts_time:[0-9.]+"
    # pts_time:20.071029
    for line in file:
        # 行を処理（改行文字を削除して表示）
        if re.search(pattern_pts, line):
            pts_times.append(re.findall(pattern_pts, line)[0])

scenes = [('0:00:00')]
for pts_time in pts_times:
    seconds=float(pts_time.replace('pts_time:',''))
    timestamp=dt.timedelta(seconds=int(seconds))
    scenes.append(str(timestamp))

# wrap up

# Print Comment

for index,scene in enumerate(scenes):
    print(f"{scene} - {ordinal(index+1)}")
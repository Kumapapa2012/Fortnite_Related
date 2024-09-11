#
# this script supports binary from https://github.com/BtbN/FFmpeg-Builds/releases

import os
import re
import argparse 
import datetime as dt
import shutil


def ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return str(n) + suffix

# ロケール設定
#import locale
#locale.setlocale(locale.LC_ALL, '')

parser = argparse.ArgumentParser(
                    prog='Fortnite Hilight Video processor',
                    description='What the program does',
                    epilog='Text at the bottom of help')

pattern = r'Fortnite (\d{4}\.\d{2}\.\d{2} - \d{2}\.\d{2}\.\d{2}\.\d{2})(\..+)?\.DVR\.mp4'
parser.add_argument('dirname')   
args = parser.parse_args()



files = sorted(os.listdir(args.dirname))
table=[]


# Command line templates
# fade in
cmdtmp1="ffmpeg -i \"{0}\" -vf \"fade=t=in:st=0:d=1\" -y output01.mp4"

# add datetime
cmdtmp2="ffmpeg -i \"output01.mp4\" -vf \"drawtext=textfile=label.txt:fontsize=64:font=Arial:borderw=5:fontcolor=white:x=(w-text_w)/2:y=(h-300)\" -y \"{0}\""

# concat
cmdtmp3="ffmpeg -safe 0 -f concat -i test_flist.txt -c copy -y output_concate_test.mp4"

# concat2 -safe way
cmdtmp3_safe='ffmpeg -i "{0}" -i "{1}" -filter_complex "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]" -map "[outv]" -map "[outa]" -y {2}'

# schene detection
cmdtmp4="ffmpeg -i output_concate_test.mp4 -vf  \"select=gt(scene\,0.3), scale=640:360,showinfo\" -vsync vfr output/%04d.jpg -f null - 2> ffout.txt"
# Command line templates


filename_tmp="Fortnite-Kills - {0}"


## START!!!

# Check filename timegap so to avoid duplicated scenes.
prev_hilight_datetime = dt.datetime(1970, 1, 1)
SAME_VIDEO_THRESHOLD=15

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
        table.append((file_name,label_text))
        prev_hilight_datetime = date_object
    else:
        #replace the last one to current one
        table.append((file_name,label_text))  if len(table) == 0 else table.__setitem__(-1, (file_name,label_text))
        #and keeps prev_hilight_datetime

for entry in table:
    
    # Phase 1 - Fade-in

    cmd1 = cmdtmp1.format( args.dirname+'\\'+entry[0])
    print("!! Running " +cmd1)
    os.system(cmd1)
    
    # Phase 2 - Timestamp in video
    
    # https://stackoverflow.com/questions/54046060/how-to-drawtext-colon-with-localtime-in-ffmpeg-filter-complex
    # due to difficulty of using ":" in drawtext, using textfile option
    with open("label.txt", "w") as file:
        file.write(entry[1])
    # cmd2 = cmdtmp2.format(args.dirname+'\\'+'processed_'+entry[0])
    cmd2 = cmdtmp2.format('processed_'+entry[0])
    print("!! Running " +cmd2)
    os.system(cmd2)

########################
# Concatinate all
########################
pattern_processed = r'processed_Fortnite (\d{4}\.\d{2}\.\d{2} - \d{2}\.\d{2}\.\d{2}\.\d{2})(\..+)?\.DVR\.mp4'

## files_processed = sorted(os.listdir(args.dirname))
files_processed = sorted(os.listdir('.'))
table = []

for file in files_processed:
    if not re.match(pattern_processed, os.path.basename(file)):
        print("ファイル名は指定されたパターンにマッチしません。: {0}".format(file))
        continue
    #table.append(args.dirname + '\\' + file)
    table.append(file)
''' old way
# Phase 1 - create a file list
with open("test_flist.txt", "w") as file:
    for entry in table:   
        strtmp="file '{0}'".format(entry)+'\n'
        strtmp=strtmp.replace("\\","\\\\") 
        file.write(strtmp)

# Phase 2 - create a concat video
cmd3=cmdtmp3
print(cmd3)
os.system(cmd3)
'''
# make 1st video
in1 = ""
for video in table:
    if in1 == "":
        in1 = "__start_placeholder_dont_delete.mp4"
    else:
        in1 = "concat_temp.mp4"
    in2 = video
    out = "output_concate_test.mp4"
    cmd3 = cmdtmp3_safe.format(in1, in2, out)
    print(cmd3)
    os.system(cmd3)
    shutil.copy(out, "concat_temp.mp4")





########################
# Wrap up
########################

# Phase 3 - scene detection
cmd4=cmdtmp4
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

scenes = [('0:00:00')]
for pts_time in pts_times:
    seconds=float(pts_time.replace('pts_time:',''))
    timestamp=dt.timedelta(seconds=int(seconds))
    scenes.append(str(timestamp))

# wrap up
dst_fname = filename_tmp.format(dt.datetime.now().strftime("%c"))
dst_fname = dst_fname.replace(":","_").replace(" ","_").replace("/","_")

# Print Comment
strchapters=""
for index,scene in enumerate(scenes):
    strchapters=strchapters+f"{scene} - {ordinal(index+1)}"+'\n'

# copy video file 
print("copying video file...")
shutil.copy2("output_concate_test.mp4",args.dirname+"\\"+dst_fname+".mp4")

# create comment file
print("creating video comment...")
comment_v=''
with open('fortnite_kills_comment_template.txt', "r") as file_c1:
    comment_v = file_c1.read()
    comment_v=comment_v.format(strchapters)
    with open(args.dirname+'\\'+dst_fname+".txt", "w") as file_c2:
        file_c2.write(comment_v)

print("Done!!!!!")
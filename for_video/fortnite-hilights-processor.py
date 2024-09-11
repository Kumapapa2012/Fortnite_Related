#
# this script supports binary from https://github.com/BtbN/FFmpeg-Builds/releases

import os
import re
import argparse 
import datetime as dt

# ロケール設定
import locale
locale.setlocale(locale.LC_ALL, '')

parser = argparse.ArgumentParser(
                    prog='Fortnite Hilight Video processor',
                    description='What the program does',
                    epilog='Text at the bottom of help')

pattern = r'Fortnite (\d{4}\.\d{2}\.\d{2} - \d{2}\.\d{2}\.\d{2}\.\d{2})(\..+)?\.DVR\.mp4'
parser.add_argument('dirname')   
args = parser.parse_args()



files = sorted(os.listdir(args.dirname))
table=[]

cmdtmp1="ffmpeg -i \"{0}\" -vf \"fade=t=in:st=0:d=1\" -y output01.mp4"
cmdtmp2="ffmpeg -i \"output01.mp4\" -vf \"drawtext=textfile=label.txt:fontsize=64:font=Arial:borderw=5:fontcolor=white:x=(w-text_w)/2:y=(h-300)\" -y \"{0}\""


for file in files:
    if not re.match(pattern, os.path.basename(file)):
        print("ファイル名は指定されたパターンにマッチしません。: {0}".format(file))
        continue

    file_name=os.path.basename(file)

    #   extract date and timestamp
    #   create text to be rendered on the video
    date_matches = re.findall(pattern, file_name)

    date_format = "%Y.%m.%d - %H.%M.%S.%f"
    date_object = dt.datetime.strptime(date_matches[0][0], date_format)
    label_text = date_object.strftime("%Y/%m/%d-%X")

    table.append((file_name,label_text))

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

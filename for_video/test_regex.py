import argparse 
import re


# Parser
parser = argparse.ArgumentParser(
                    prog='Fortnite Video Uploader',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('filename')   

args=parser.parse_args()

# 正規表現パターン
pattern = r'Fortnite \d{4}\.(\d{2}\.\d{2}) - (\d{2}\.\d{2}\.\d{2}\.\d{2})(\..+)?\.DVR\.mp4'

# チェックするファイル名
#file_name = 'Fortnite 2024.05.13 - 18.21.20.00.Gameplay.DVR.mp4'
file_name = args.filename

# パターンに一致するかチェック
if re.match(pattern, file_name):
    print("ファイル名は指定されたパターンにマッチします。")
else:
    print("ファイル名は指定されたパターンにマッチしません。")

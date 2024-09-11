import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2 import credentials 
from google.auth.transport.requests import Request

import argparse 

import os
import re

# user token to save
user_token = "token_file.json"

# Parser
parser = argparse.ArgumentParser(
                    prog='Fortnite Video Uploader',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('filename')   
args = parser.parse_args()

# パターンに一致するかチェック
pattern = r'Fortnite (\d{4}\.\d{2}\.\d{2}) - (\d{2}\.\d{2}\.\d{2}\.\d{2})(\..+)?\.DVR\.mp4'
file_name = os.path.basename(args.filename)

if re.match(pattern, file_name):
    print("ファイル名は指定されたパターンにマッチします。")
else:
    print("ファイル名は指定されたパターンにマッチしません。")
    exit(2)

match=re.search(pattern,file_name)
file_data = {
    "date_time" : match.group(1)+"-"+match.group(2),
    "scene" : "Full" if match.group(3) is None else match.group(3).replace('.','')
}

# 動画のタイトルと説明をJSONファイルから読み込む
with open('video_details.json', 'r', encoding='utf-8') as f:
    video_details = json.load(f)

# 
title = video_details["title"].format(file_data['scene'],file_data['date_time'])
description = video_details["description"].format(file_data['date_time'])

print(title)
print(description)

# start uploading

scopes = ["https://www.googleapis.com/auth/youtube.upload"]

# JSONファイルから認証情報を読み込む
creds=None
if os.path.exists(user_token):
    creds = credentials.Credentials.from_authorized_user_file(user_token, scopes)

# If there are no (valid) user credentials available, prompt the user to log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", scopes)
        creds = flow.run_local_server(port=8080)
    # Save the credentials for the next run
    with open(user_token, 'w') as token:
        token.write(creds.to_json())
# YouTube APIクライアントを構築
youtube = googleapiclient.discovery.build(
    "youtube", "v3", credentials=creds)



# アップロードする動画の情報を設定
request_body = {
    "snippet": {
        "categoryId": "22",
        "title": title,
        "description": description,
        "tags": ["sample", "video", "api"]
    },
    "status": {
        "privacyStatus": "public"
    }
}

# ファイルをアップロード
media_body = googleapiclient.http.MediaFileUpload(args.filename, chunksize=-1, resumable=True)
request = youtube.videos().insert(
    part="snippet,status",
    body=request_body,
    media_body=media_body
)

# Wait for completion
response = None
while response is None:
    # This doesn't work if chunksize=-1!! But it's OK!! chunksize=-1 is the fastest.
    status, response = request.next_chunk()
    if status:
        
        print("アップロード中: {0:.2f}%".format(status.progress() * 100))

print("アップロード完了！")

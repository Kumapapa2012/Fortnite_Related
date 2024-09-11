@echo off
for %%A in (%*) do (
    echo Processing file: %%A
    REM ここにファイルを処理するコードを書きます。例えば:
    REM python3 "C:\Users\morim\Documents\__kmori_tools\Youtube_Uploader_Fortnite\fortnite_yt_upload.py" "%%A"
    echo %%A >> "C:\Users\morim\Documents\__kmori_tools\Youtube_Uploader_Fortnite\file_list.txt"
)

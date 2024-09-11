@echo off
setlocal enabledelayedexpansion

REM Sort file_list.txt
set FILE="%CD%\file_list.txt"
echo %FILE%
if not exist %FILE% (
    echo "Not exist file_list.txt"
    pause
    exit
)

set SORTED="file_list_sorted.txt"
type %FILE% | sort > file_list_sorted.txt

for /f "delims==''" %%A in ('type %SORTED%') do (
    set FILEPATH=%%A
    echo ======== Uploading !FILEPATH! ========
    python3 fortnite_yt_upload.py !FILEPATH!
    if not errorlevel 1 (
        echo %%A >> upload_failed.txt
    )
    echo Sleeping for 30 seconds...
    timeout /t 30
)


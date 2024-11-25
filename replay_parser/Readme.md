# Fortnite Replay Paser Sample Code
Outputs Kill Timestamps from specified Replay File and Epic Id

## Usage
_Fortnite.exe <Replay_File_Path> <Epic_Id> <Offset>

### Replay_File_Path : Path to .replay file 
("%localappdata%\FortniteGame\Saved\Demos\UnsavedReplay-XXXXXXXX.replay")

### Epic_Id : Epic Id to get the kills for.
("aaaabbbbccccddddeeeeffff00001111")

### Offset : Adds specified seconds to actual kill timing
("-5")

## Output
```
 1st : 02:29
 2nd : 03:17
 3rd : 04:12
 4th : 06:59
 5th : 08:12
 6th : 08:19
 7th : 10:40
 8th : 12:49
 9th : 12:59
10th : 18:03
11th : 22:36
12th : 23:06
```

## Build
1. Clone the repo
2. Open the folder cloned with vscode
3. Run debugger using F5 to get Debug build.
4. Run "dotnet publish --configuration Release" in built-in Terminal to get Release Build.

   
Only .net 9.0, win-x64 target is in this project. If you need binary for  other target, add what you want by yourself.

## References
- FortniteReplayReader
https://www.nuget.org/packages/FortniteReplayReader
- Unreal.core
https://www.nuget.org/packages/Unreal.Core

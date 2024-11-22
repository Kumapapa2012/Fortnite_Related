﻿using System;
using System.Linq;
using System.Runtime.CompilerServices;
using FortniteReplayReader;

// See https://aka.ms/new-console-template for more information
// Thanks to https://github.com/Shiqan/FortniteReplayDecompressor/tree/master
// To make release buid, run
// > dotnet publish --configuration Release
// To deploy(for me)
// > cp bin\Release\net9.0\win-x64\publish\_Fortnite.exe C:\Users\morim\kmori_bin

static string FormNumber(int num)
{
    if( num <= 0 ) return num.ToString();
    var sp="";
    if( num < 10 ) sp = " ";

    switch(num % 100)
    {
        case 11:
        case 12:
        case 13:
            return sp + num + "th";
    }
    
    switch(num % 10)
    {
        case 1:
            return sp + num + "st";
        case 2:
            return sp + num + "nd";
        case 3:
            return sp + num + "rd";
        default:
            return sp + num + "th";
    }
}

const int TIME_OFFSET = -5;
var replayFile = "C:\\Users\\morim\\Documents\\_Fortnite\\UnsavedReplay-2024.09.07-03.30.12.replay";
var myEpicId = "4679c513a0614c889148f61ec69aa749";
var offset=TIME_OFFSET;

// override replayFile and myEpicId
if(args.Length > 0 ){
    replayFile = args[0];
    Console.WriteLine("replayFile has been overridden by cmdline");
    if(args.Length > 1 ) {
        myEpicId = args[1];
        Console.WriteLine("myEpicId has been overridden by cmdline");
        if(args.Length > 2 ) {
            if (Int32.TryParse(args[2], out int j))
            {
                offset = j;
                Console.WriteLine("offset has been overridden by cmdline");
            }
            else
            {
                Console.WriteLine("String could not be parsed for offset.");
                Environment.Exit(1);
            }            
        }
    }
}

var reader = new ReplayReader();
var replay = reader.ReadReplay(replayFile);
var myKills = replay.Eliminations.Where(c => c.Eliminator == myEpicId.ToUpper()).ToList();

for (var i = 0; i < myKills.Count() ; i++)
{
    var killedAt = DateTime.ParseExact(myKills[i].Time, "mm:ss",null);
    Console.WriteLine( FormNumber(i + 1) + " : " + killedAt.AddSeconds(offset).ToString("mm:ss") );  
} 
// Console.WriteLine(args);
// Console.WriteLine(args.Length);

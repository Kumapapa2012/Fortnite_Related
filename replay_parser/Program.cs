using FortniteReplayReader;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Unicode;

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
var replayData_json_path="";

// Cmdline args : overrides defaults
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
            if(args.Length > 3 ) {
                replayData_json_path = args[3];
            }            
        }
    }
}
else {
    Console.WriteLine("Usage: _Fortnite.exe <replay_file_path> <Epic_Id> <offset> <json_dump_path>");
    Console.WriteLine("<replay_file_path>: Replay File Path (normally stred in 'C:\\Users\\morim\\AppData\\Local\\FortniteGame\\Saved\\Demos')");
    Console.WriteLine("<Epic_Id>: EpidId for Kill Event List");
    Console.WriteLine("<offset>: Seconds to add to kill event timestamp(i.e. -5)");
    Console.WriteLine("<json_dump_path>: File Path to extract replay data in JSON format.");
    Environment.Exit(0);
}

// read replays
var reader = new ReplayReader();
var replay = reader.ReadReplay(replayFile);

// write json if the path was specified.
if(replayData_json_path != ""){
    using (var sw = new StreamWriter(replayData_json_path, false, System.Text.Encoding.UTF8))
    {
        var json_options = new JsonSerializerOptions
        {
            Encoder = JavaScriptEncoder.Create(UnicodeRanges.All),
            NumberHandling = System.Text.Json.Serialization.JsonNumberHandling.AllowNamedFloatingPointLiterals,
            WriteIndented = true
        };
        var jsonString = JsonSerializer.Serialize(replay, json_options);

        // JSON データをファイルに書き込み
        sw.Write(jsonString);
    }
}

// Parse replay data
Console.WriteLine("======== Match Data from the Replay File of the Match. ========");

// Match Date Time
if (replay.GameData.UtcTimeStartedMatch.HasValue){
    var started_at = replay.GameData.UtcTimeStartedMatch.Value.ToLocalTime();
    Console.WriteLine(String.Format("Started at : {0}" ,started_at));
    Console.WriteLine(String.Format("Ended at : {0}" ,started_at.AddSeconds(replay.GameData.MatchEndTime ?? 0)));
}

// PlayerData : Placement == null : NPCs , Placement != null : Players
var playerData_except_NPCs = replay.PlayerData.Where(o => o.Placement != null);
Console.WriteLine(String.Format("Total Players: {0}",playerData_except_NPCs.Count()));

var real_players = playerData_except_NPCs.Where(o => o.IsBot == false);
Console.WriteLine(String.Format("Real Players : {0} / Bots : {1}"
                ,real_players.Count()
                ,playerData_except_NPCs.Count() - real_players.Count()
                ));


// Kills
Console.WriteLine("Eliminations performed by the player.");
var myEliminations = replay.Eliminations.Where(c => c.Eliminator == myEpicId.ToUpper()).ToList();
for (var i = 0; i < myEliminations.Count() ; i++)
{
    var killedAt = DateTime.ParseExact(myEliminations[i].Time, "mm:ss",null);

    var killedPlayerData = replay.PlayerData.Where( d => d.PlayerId == myEliminations[i].EliminatedInfo.Id.ToUpper()).ToList();
    var botKill = false;
    if(killedPlayerData.Count() > 0 && killedPlayerData[0].IsBot) {
        botKill = true;
    }
    //Console.WriteLine( FormNumber(i + 1) + " : " + killedAt.AddSeconds(offset).ToString("mm:ss") );  
    Console.WriteLine( String.Format("{0}: {1} - {2}"
        , FormNumber(i + 1)
        , killedAt.AddSeconds(offset).ToString("mm:ss")
        , botKill ? "bot" : "human"));  
} 
// Console.WriteLine(args);
// Console.WriteLine(args.Length);

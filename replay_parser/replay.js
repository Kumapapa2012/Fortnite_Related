const fs = require('fs');
const parseReplay = require('fortnite-replay-parser');
const replayBuffer = fs.readFileSync('UnsavedReplay-2024.10.19-17.00.15.replay');

const config = {
  parseLevel: 10,
  debug: true,
}

parseReplay(replayBuffer, config).then((parsedReplay) => {
  fs.writeFileSync('replayData.json', JSON.stringify(parsedReplay, null , 2));
}).catch((err) => {
  console.error('An error occured while parsing the replay!', err);
});
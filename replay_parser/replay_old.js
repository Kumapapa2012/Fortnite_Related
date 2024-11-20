const fs = require('fs');
const parseReplay = require('fortnite-replay-parser');
const replayBuffer = fs.readFileSync('kmori-victryroyale20241119.replay');
const config = {
  parseLevel: 10,
  debug: true,
}

parseReplay(replayBuffer, config).then((parsedReplay) => {
  fs.writeFileSync('replayData.json', JSON.stringify(parsedReplay));
}).catch((err) => {
  console.error('An error occured while parsing the replay!', err);
});
const ytdl = require('@distube/ytdl-core');
const fs = require('fs');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question("Enter the YouTube video URL: ", (videoURL) => {
  // Check if the URL is valid
  if (!ytdl.validateURL(videoURL)) {
    console.log("Invalid YouTube URL.");
    rl.close();
    return;
  }

  console.log("Downloading audio...");

  // Create a writable stream for saving the audio file
  const audioStream = fs.createWriteStream('audio.mp3');

  // Download the audio and save it as .mp3
  ytdl(videoURL, { filter: 'audioonly' })
    .pipe(audioStream)
    .on('finish', () => {
      console.log("Audio downloaded as audio.mp3.");
      rl.close();
    })
    .on('error', (err) => {
      console.error('Error downloading the audio:', err);
      rl.close();
    });
});



const express = require('express');
const ytdl = require('@distube/ytdl-core');
const fs = require('fs');
const path = require('path');
const cors = require('cors');  // Import CORS

const app = express();
const port = 3000;

// Use CORS middleware to allow cross-origin requests
app.use(cors());

// Middleware to parse JSON requests
app.use(express.json());

// Serve static files (frontend)
app.use(express.static(path.join(__dirname, '../frontend')));

// Endpoint to handle the audio download request
app.post('/download-audio', (req, res) => {
  const videoURL = req.body.url;

  if (!ytdl.validateURL(videoURL)) {
    return res.json({ success: false, message: 'Invalid YouTube URL.' });
  }

  // Define the path for the audio file
  const audioPath = path.join(__dirname, 'audio.mp3');

  // Create a writable stream for saving the audio file
  const audioStream = fs.createWriteStream(audioPath);

  // Download the audio and save it as .mp3
  ytdl(videoURL, { filter: 'audioonly' })
    .pipe(audioStream)
    .on('finish', () => {
      res.json({ success: true, message: 'Audio is downloading...' });
    })
    .on('error', (err) => {
      console.error('Error downloading audio:', err);
      res.json({ success: false, message: 'Error downloading audio.' });
    });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

module.exports = app;

document.getElementById('start-download').addEventListener('click', () => {
    const videoURL = document.getElementById('video-url').value;
  
    // Check if URL is valid
    if (!isValidYouTubeURL(videoURL)) {
      alert("Invalid YouTube URL.");
      return;
    }
  
    // Show loading spinner
    document.getElementById('loading').style.display = 'block';
    document.getElementById('notification').style.display = 'none'; // Hide notification initially
  
    // Make an API call to download the audio (backend)
    fetch('http://localhost:3000/download-audio', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: videoURL })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Download started, but we wait until it's finished
        setTimeout(() => {
          document.getElementById('loading').style.display = 'none';
          document.getElementById('notification').style.display = 'block';
        }, 5000); // Show notification after 5 seconds (adjust this based on actual download time)
      } else {
        alert(data.message);
        document.getElementById('loading').style.display = 'none'; // Hide loading if error
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Something went wrong.');
      document.getElementById('loading').style.display = 'none'; // Hide loading on error
    });
  });
  
  function isValidYouTubeURL(url) {
    // Simple YouTube URL validation
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/.+$/;
    return youtubeRegex.test(url);
  }
  
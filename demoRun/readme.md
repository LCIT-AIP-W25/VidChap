# Vidchap Setup Guide 


### Prerequisites : 
  - Do this before running
    - Download and setup Git (https://git-scm.com/)
    - Go to command Prompt and type 
      ```bash
      git clone https://github.com/LCIT-AIP-W25/VidChap
      cd vidchap
      ```
    - Download the vosk model - [vosk-model-small-en-us-0.15] from their official website (https://alphacephei.com/vosk/models) and paste it into the demoRun directory replacing the empty folder.
    - Then go to command prompt and type 
      ```bash
      python -m pip install -r requirements.txt 
      winget install ffmpeg ```
      [ if the winget command doesnt work then install winget first and then run the above command or go to the official website to see more download options (https://www.gyan.dev/ffmpeg/builds) and make sure to add the ffmpeg path to your environment variables ]
      

### Running :
  - For Frontend Application Full
      ```bash
      streamlit run app.py
      ```
  - For Backend (Only Generating the data and saving it)
      ```bash
      python main.py
      ```
    
    

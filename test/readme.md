# README for Testing Framework

## Overview
This project involves testing the functionality of a Python-based backend and a Streamlit-based frontend application. The application processes YouTube video URLs, downloads audio files, converts them to WAV format, and provides an intuitive user interface for interaction. This README covers the testing details for **Test Cycle 1** and outlines the plan for **Test Cycle 2**.

---

## Test Cycle 1: Summary

### Backend Testing
- **Link Processing**: Validated the extraction of video IDs from various YouTube URL formats.
- **Audio Downloading**: Ensured audio files were successfully downloaded from YouTube.
- **File Conversion**: Verified MP3-to-WAV conversion, including handling corrupted or invalid files.

### Frontend Testing
- **UI Rendering**: Confirmed sidebar components (logo, navigation buttons, and user profile section) rendered correctly.
- **URL Input Functionality**: Tested that input fields processed user-provided URLs accurately and updated the session state.
- **Frontend-Backend Communication**: Verified smooth interaction between frontend actions and backend processes.

---

## How to Run Tests

### Backend Testing

#### Step 1: Navigate to the Test Directory
```bash
cd tests/
```

#### Step 2: Install Dependencies
Make sure all required libraries are installed:
```bash
pip install -r requirements.txt
```

#### Step 3: Execute Backend Tests
Run the tests using `pytest`:
```bash
pytest
```

#### Backend Features Tested:
1. **`extract_video_id(url)`**: Ensures proper video ID extraction from various YouTube URL formats.
2. **Audio Download**: Simulates downloading audio and verifies that the file is valid.
3. **`convert_mp3_to_wav(mp3_path, wav_path)`**: Tests conversion functionality and handles corrupted audio files.

### Frontend Testing

#### Step 1: Start Backend Server
Navigate to the `backend/` folder and start the server:
```bash
cd backend/
python app.py
```

#### Step 2: Execute Frontend Tests
Navigate to the test directory and run frontend tests using Streamlit's testing module:
```bash
python -m pytest frontend_tests.py
```

#### Frontend Features Tested:
1. Sidebar components: Logo, navigation buttons, and user profile section.
2. URL input processing and session state updates.
3. Download button interaction and success message display.

---

## Test Cycle 2: Planned Enhancements

### Backend
1. **Improved Error Handling**: Test edge cases for invalid YouTube links and network errors during audio download.
2. **File Validation**: Validate file types and integrity after downloading.
3. **Scalability**: Stress-test the backend with multiple simultaneous requests.

### Frontend
1. **Dynamic Feedback**: Ensure real-time feedback for invalid URLs.
2. **Enhanced UI Testing**: Validate responsiveness and accessibility for various devices.
3. **Advanced Interaction**: Test complex workflows, such as multiple file uploads.

---

## Additional Notes
- **Temporary Files**: Temporary audio files (e.g., `.mp3` or `.wav`) are automatically cleaned up at the end of each test session.
- **Dependencies**: Ensure Python libraries listed in `requirements.txt` are installed before running tests.

---

## Completed in Test Cycle 1
- Backend URL and audio functionality.
- Frontend input processing and feedback flow. 

## Upcoming in Test Cycle 2
- Error handling for invalid input.
- Stress testing for backend scalability.
- Dynamic UI validation for improved user experience.

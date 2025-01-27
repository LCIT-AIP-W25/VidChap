
# Test Cycle 1
## Test Cases

### Backend
- **Link Processing**: Verify that the given link by the user is being processed correctly.
- **Invalid Links**: Ensure that invalid links are handled properly.
- **Audio Downloading**: Check if the audio file from the YouTube video is downloaded correctly.

### Frontend
- **Website Loading & Styling**: Test that the website loads properly and follows the structure defined in "Design-Action-1".
- **Upload Button Functionality**: Ensure the upload button handles data properly, including invalid data.
- **Frontend-Backend Communication**: Verify that the frontend successfully communicates with the backend.

---

## Backend Testing

### Step 1: Navigate to the `test/` folder
Make sure you are in the correct directory before running the backend tests.

```bash
cd test/
```

### Step 2: Run the Backend Tests

Use `Mocha` to run the backend tests.

```bash
npx mocha backend.test-1.js
```

This will run the following tests:
- Validating that the link entered by the user is being processed correctly.
- Handling invalid links.
- Ensuring that the audio file is downloaded properly from YouTube.

---

## Frontend Testing

### Step 1: Start the Backend Server

Before testing the frontend, make sure the backend server is running. Navigate to the `backend/` folder and run the following command to start the server.

```bash
cd backend/
node da.js
```

This will start the server that handles the frontend requests.

### Step 2: Navigate to the `test/` folder
Ensure you are in the `test/` folder before running the frontend test.

```bash
cd test/
```

### Step 3: Run the Frontend Tests

Now, you can run the frontend tests using Python and Selenium.

```bash
python frontend-test-1.py
```

This test will:
- Check if the website is loading properly with the correct styling and structure.
- Verify if the upload button is functioning properly and handling both valid and invalid data.
- Ensure that the frontend is transmitting data to the backend correctly.

---

## Additional Notes

- **Backend Testing**: The backend tests check the API endpoints and their responses when a user submits a valid or invalid YouTube link. The tests also verify if the audio is downloaded correctly.
- **Frontend Testing**: The frontend tests ensure that the user interface works as expected, from loading the website to interacting with the upload button. It also verifies if the frontend properly communicates with the backend API.

## Completed 
- No
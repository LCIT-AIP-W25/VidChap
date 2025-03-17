import requests
import pytest

# Define the API endpoint
API_URL = "http://localhost:8000/process-youtube"

# Test cases for functional testing
test_cases = [
    ("https://youtu.be/HG68Ymazo18?si=gMuR74pG9iVvCaC-", 200),
    ("https://youtu.be/DzbFBgGUGdU?si=0r9CGYWuaBYMqulx", 200),
    ("invalid_url", 500),
    ("https://www.youtube.com/watch?v=nonexistent", 500),
]

@pytest.mark.parametrize("url, expected_status", test_cases)
def test_functional(url, expected_status):
    payload = {"url": url}
    response = requests.post(API_URL, json=payload)
    assert response.status_code == expected_status
    if expected_status == 200:
        assert "full_transcript" in response.json()
        assert "chapters" in response.json()
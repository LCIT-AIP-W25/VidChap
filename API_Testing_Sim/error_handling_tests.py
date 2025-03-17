import requests

API_URL = "http://localhost:8000/process-youtube"

def test_error_handling():
    # Test with no URL provided
    response = requests.post(API_URL, json={})
    assert response.status_code == 422

    # Test with an empty URL
    response = requests.post(API_URL, json={"url": ""})
    assert response.status_code == 500
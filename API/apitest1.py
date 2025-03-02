import requests

# define the API endpoint and payload
url = "http://localhost:8000/process-youtube"
payload = {
    "url": "https://www.youtube.com/watch?v=jmmW0F0biz0"
}

#https://www.youtube.com/watch?v=jmmW0F0biz0"
#https://youtu.be/AycTgPJtBP0?si=FtPjZ1bNuxwQO2EC

# send the POST request
response = requests.post(url, json=payload)

# print the response
if response.status_code == 200:
    print("Transcript and Chapters:")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)

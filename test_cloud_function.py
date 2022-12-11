import requests
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Set the URL of your Cloud Function
function_url = os.getenv('CLOUD_FUNCTION_URL')

# Set the input data for your Cloud Function
data = {
    "calls": [
        ["190.61.88.147"],
        ["139.99.237.62"],
        ["20.111.54.16"],
        ["185.143.146.171"],
        ["121.126.20.41"],
    ]
}

# Use the requests library to make a POST request to your function
response = requests.post(function_url, json=data)

# Print the response from your function
print(response.json())

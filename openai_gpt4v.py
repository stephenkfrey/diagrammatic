import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()
# Set your OpenAI API key here
api_key = os.getenv("OPENAI_API_KEY")

def encode_image(image_path):
    """
    Encodes the given image to base64.
    
    Args:
    - image_path: The path to the image file.
    
    Returns:
    - The base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def is_diagram_check_gpt4v(image_path):
    """
    Checks if the given image is a diagram or not using GPT-4-vision.
    
    Args:
    - image_path: The path to the image file.
    
    Returns:
    - True if the image is a diagram, False otherwise.
    """
    try:
        base64_image = encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Is this a diagram? Please respond 'yes' or 'no'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_data = response.json()
        
        # Assuming the response structure allows direct access to the answer
        # This might need adjustment based on actual API response
        answer = response_data['choices'][0]['message']['content'].lower()
        print(f"Answer: {answer}")
        return "yes" in answer
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage
# image_path = 'output_figures/dl15/diagrams/Element 158.png'
# if is_diagram_check_gpt4v(image_path):
#     print("The image is a diagram.")
# else:
#     print("The image is not a diagram.")
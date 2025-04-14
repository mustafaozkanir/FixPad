import requests
import base64
import os

omniparser_api_key = os.getenv("INFERENCE_API_KEY_OMNIPARSER")

def get_parsed_image_content(image_path):
    """
    Sends a screenshot image to the OmniParser v2 API and returns detected UI elements.

    Args:
        image_path (str): Path to the image file.

    Returns:
        list: A list of detected elements from the image.
    """
        
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')

    headers = {
        'Authorization': f'Bearer {omniparser_api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
            "model": "omniparser2",
            "base64_image": image_data,
            "box_threshold": 0.5,
            "iou_threshold": 0.5,
            "text_threshold": 0.2
    }

    response = requests.post(
        'https://api.inferenceapis.com',
        json=payload,
        headers=headers
    )

    parsed_data = response.json()
    """
        Returns only the detected elements.
        If you also want to return image content either return parsed_data as whole
        and access the image with parsed_data['processed_image']
        and detected elements as parsed_data['detected_elements']
    """
    # print(parsed_data["detected_elements"])
    return parsed_data["detected_elements"], parsed_data['processed_image']
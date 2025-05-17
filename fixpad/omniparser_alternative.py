# omniparser.py

import replicate
import requests
import os
import base64
import signal
import sys
import time
from dotenv import load_dotenv

# Load token
load_dotenv()
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

# Cancel URL tracker
pending_cancel_url = None

def handle_exit(sig, frame):
    global pending_cancel_url
    if pending_cancel_url:
        print("🛑  Cancelling in-flight prediction...")
        try:
            response = requests.post(
                pending_cancel_url,
                headers={"Authorization": f"Token {replicate_api_token}"}
            )
            if response.status_code == 200:
                print("✅  Prediction cancelled.")
            else:
                print(f"⚠️  Cancel failed (status {response.status_code})")
        except Exception as e:
            print(f"❌  Cancel error: {e}")
    else:
        print("ℹ️  No active prediction to cancel.")
    sys.exit(0)

# Register Ctrl+C and termination handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

def get_parsed_image_content(image_path):
    global pending_cancel_url

    with open(image_path, "rb") as f:
        image_data_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

    print("📡 Creating prediction...")
    prediction = replicate.predictions.create(
        version="49cf3d41b8d3aca1360514e83be4c97131ce8f0d99abfc365526d8384caa88df",
        input={
            "image": image_data_uri,
            "box_threshold": 0.05,
            "iou_threshold": 0.7,
            "imgsz": 1280,
            "text_threshold": 0.8,
            "use_paddleocr": True 
        }
    )

    get_url = prediction.urls["get"]
    pending_cancel_url = prediction.urls["cancel"]

    print(f"⏳  Waiting for result... (Prediction ID: {prediction.id})")

    # Manual polling loop
    while True:
        time.sleep(1)
        prediction = requests.get(
            get_url,
            headers={"Authorization": f"Token {replicate_api_token}"}
        ).json()

        status = prediction.get("status", "unknown")
        if status in ["succeeded", "failed", "canceled"]:
            break

    pending_cancel_url = None  # Reset

    if status != "succeeded":
        print(f"❌  Prediction ended with status: {status}")
        return [], None

    output = prediction["output"]

    # Parse UI elements
    raw_elements = output.get("elements", "")
    try:
        elements = []
        for line in raw_elements.strip().split("\n"):
            obj = eval(line.split(": ", 1)[1])
            elements.append(obj)
    except Exception as e:
        print(f"⚠️  Failed to parse elements: {e}")
        elements = []

    # Download processed image
    img_url = output.get("img")
    image_content = None
    if img_url:
        try:
            r = requests.get(img_url)
            if r.status_code == 200:
                image_content = base64.b64encode(r.content).decode("utf-8")
            else:
                print(f"⚠️  Failed to fetch image (status {r.status_code})")
        except Exception as e:
            print("⚠️  Download error:", e)

    return elements, image_content

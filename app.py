"""Bata Figurine Generator - Flask app that transforms photos into
collectible figurines using Gemini AI."""
import base64
import io
import os
import tempfile
import time
import traceback

from flask import Flask, render_template, request, jsonify, send_from_directory, abort
import requests
import qrcode
from PIL import Image

# Import the API keys directly from the config file
try:
    from config import IMGBB_API_KEY, GEMINI_API_KEY
except ImportError:
    # Handle missing config.py for CI/CD or fresh installs
    IMGBB_API_KEY = None
    GEMINI_API_KEY = None

# Import the Google Generative AI library
from google import genai

# Configure the Gemini API with your key
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_favicon(filename):
    """Serve favicon files from the favicon folder"""
    favicon_files = [
        'favicon.ico', 'favicon.svg', 'favicon-96x96.png',
        'apple-touch-icon.png', 'site.webmanifest'
    ]
    if filename in favicon_files:
        return send_from_directory('favicon', filename)
    abort(404)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    """Flask route to upload an existing photo, transform with Gemini, and generate QR"""
    print("Received a request to /upload_photo")
    try:
        file = request.files.get('file')

        if not file:
            print("Error: No file part in the request.")
            return jsonify({'success': False, 'error': 'No file uploaded'})

        print(f"Original file received: {file.filename}")

        # Save original file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as original_temp_file:
            file.save(original_temp_file.name)
            original_temp_path = original_temp_file.name

        print(f"Original file saved temporarily at: {original_temp_file.name}")

        generated_image_data = generate_image_with_gemini(original_temp_path)

        if not generated_image_data:
            os.unlink(original_temp_path)
            return jsonify({'success': False, 'error': 'AI transformation failed.'})

        print("Gemini transformation successful")

        # 2. Save the generated image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as generated_temp_file:
            with open(generated_temp_file.name, 'wb') as f:
                f.write(generated_image_data)
            generated_temp_path = generated_temp_file.name

        print(f"Generated image saved temporarily at: {generated_temp_file.name}")

        # 3. Upload the generated image to ImgBB
        print("Uploading generated image to ImgBB...")
        final_imgbb_url, _ = upload_to_imgbb(generated_temp_path, IMGBB_API_KEY)

        # Clean up temp files
        os.unlink(original_temp_path)
        os.unlink(generated_temp_path)

        if not final_imgbb_url:
            return jsonify({
                'success': False,
                'error': 'Failed to upload generated image to ImgBB.'
            })

        print(f"Generated image ImgBB URL: {final_imgbb_url}")

        # 4. Generate QR code for the final image URL
        print("Generating QR code for the generated image...")
        qr_code_data = generate_qr_code(final_imgbb_url)

        print(f"Final results - image_url: {final_imgbb_url}, "
              f"qr_code_data: {qr_code_data is not None}")

        if final_imgbb_url and qr_code_data:
            return jsonify({
                'success': True,
                'image_url': final_imgbb_url,
                'qr_code': qr_code_data
            })

        return jsonify({
            'success': False,
            'error': 'Failed to generate QR code'
        })

    except (OSError, ValueError, requests.RequestException) as e:
        print(f"Error in upload_photo: {e}")
        # Clean up temp files if they exist
        for temp_file in ['original_temp_file', 'generated_temp_file']:
            if temp_file in locals():
                try:
                    os.unlink(locals()[temp_file].name)
                except OSError:
                    pass
        return jsonify({
            'success': False,
            'error': str(e)
        })

def generate_image_with_gemini(input_image_path):
    """Generate image using Gemini AI with retry logic."""
    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            # Read the image file and create a PIL Image object
            img = Image.open(input_image_path)

            prompt = (
                "A 1/7 scale collectible figure of a vintage shoe company employee "
                "inspired by the provided photo dressed as a shoemaker. "
                "Change the background to an office with solid wooden furniture "
                "and tools for shoe making. The figure is on a classic wooden desk "
                "with retro shoe samples and ledgers. The figure is on a circular "
                "transparent acrylic base with a retro-style collectible box next "
                "to it that says 'Bata' in bold red letters."
            )

            print(f"Gemini API attempt {attempt + 1}/{max_retries + 1}")

            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt, img]
            )

            # Check if response has candidates
            if not response.candidates or len(response.candidates) == 0:
                raise ValueError("No candidates returned from Gemini API")

            # Iterate through parts to find and extract image data
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(part.text)
                if hasattr(part, "inline_data") and part.inline_data:
                    # Get the image data from the part
                    image_data = part.inline_data.data
                    return image_data

            print("No image data found in the response.")
            return None

        except (ValueError, TypeError, AttributeError) as e:
            error_str = str(e)
            print(f"Error during Gemini image generation (attempt {attempt + 1}): {e}")

            # Check if it's a 500 error and we have retries left
            if "500" in error_str and attempt < max_retries:
                print(f"500 error detected, waiting 10 seconds before retry... "
                      f"({attempt + 1}/{max_retries})")
                time.sleep(10)
                continue

            # Final attempt or non-500 error
            traceback.print_exc()
            return None

    return None

def upload_to_imgbb(file_path, api_key):
    """Upload image to ImgBB and return URL."""
    try:
        with open(file_path, 'rb') as file:
            image_data = base64.b64encode(file.read()).decode('utf-8')

        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": image_data,
        }

        response = requests.post(url, data=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result['success']:
                image_url = result['data']['url']
                return image_url, None
            print(f"ImgBB API error: {result.get('error', 'Unknown error from ImgBB')}")
            return None, None

        print(f"HTTP error uploading to ImgBB: {response.status_code}, "
              f"body: {response.text}")

        return None, None

    except requests.RequestException as e:
        print(f"Error uploading to ImgBB: {e}")
        return None, None

def generate_qr_code(url):
    """Generate QR code and return as base64 string"""
    try:
        print(f"Generating QR code for URL: {url}")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_code_data = base64.b64encode(img_buffer.getvalue()).decode()

        print("QR code generated successfully")
        return qr_code_data

    except (OSError, ValueError) as e:
        print(f"Error generating QR code: {e}")
        return None

if __name__ == '__main__':
    print("🚀 Bata Figurine Generator with Gemini AI")
    print("Open your browser and go to: http://localhost:8080")
    print("Make sure your Gemini and ImgBB API keys are valid in config.py")

    # Check essential files
    if not os.path.exists('templates/index.html'):
        print("Error: templates/index.html not found")
    if not os.path.exists('static/mdc.jpg'):
        print("Error: static/mdc.jpg not found")
    if not os.path.exists('config.py'):
        print("Error: config.py not found - add your API keys")

    app.run(debug=True, host='0.0.0.0', port=8080)

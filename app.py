from flask import Flask, render_template, request, jsonify
import tempfile
import os
import requests
import qrcode
from PIL import Image
import base64
import io
from config import IMGBB_API_KEY, GEMINI_API_KEY
from dotenv import load_dotenv
import os

load_dotenv()

# Import the Google Generative AI library and its types
import google.generativeai as genai

app = Flask(__name__)

# --- API Keys ---
# Your hardcoded ImgBB API key
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
# Your Gemini API Key (IMPORTANT: Replace with your actual key)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini API client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-image-preview")

# Set generation and safety configurations
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
# Adjusted safety settings to prevent image blocking during testing
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

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
        original_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        file.save(original_temp_file.name)
        original_temp_file.close()

        print(f"Original file saved temporarily at: {original_temp_file.name}")

        # 1. Generate transformed image using Gemini with streaming API
        # Simplified prompt to improve image generation
        transformation_prompt = """A 1/7 scale collectible figure of a vintage shoe company employee inspired by the provided photo. The figure is on a classic wooden desk with retro shoe samples and ledgers. The figure is on a circular transparent acrylic base with a retro-style collectible box next to it that says "Bata" in bold red letters."""

        generated_image_data = generate_image_with_gemini(original_temp_file.name, transformation_prompt)

        if not generated_image_data:
            os.unlink(original_temp_file.name)
            return jsonify({'success': False, 'error': 'AI transformation failed.'})

        print("Gemini transformation successful")

        # 2. Save the generated image temporarily
        generated_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        with open(generated_temp_file.name, 'wb') as f:
            f.write(generated_image_data)
        generated_temp_file.close()

        print(f"Generated image saved temporarily at: {generated_temp_file.name}")

        # 3. Upload the generated image to ImgBB
        print("Uploading generated image to ImgBB...")
        final_imgbb_url, _ = upload_to_imgbb(generated_temp_file.name, IMGBB_API_KEY)

        # Clean up temp files
        os.unlink(original_temp_file.name)
        os.unlink(generated_temp_file.name)

        if not final_imgbb_url:
            return jsonify({'success': False, 'error': 'Failed to upload generated image to ImgBB.'})

        print(f"Generated image ImgBB URL: {final_imgbb_url}")

        # 4. Generate QR code for the final image URL
        print("Generating QR code for the generated image...")
        qr_code_data = generate_qr_code(final_imgbb_url)

        print(f"Final results - image_url: {final_imgbb_url}, qr_code_data: {qr_code_data is not None}")

        if final_imgbb_url and qr_code_data:
            return jsonify({
                'success': True,
                'image_url': final_imgbb_url,
                'qr_code': qr_code_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate QR code'
            })

    except Exception as e:
        print(f"Error in upload_photo: {e}")
        # Clean up temp files if they exist
        for temp_file in ['original_temp_file', 'generated_temp_file']:
            if temp_file in locals():
                try:
                    os.unlink(locals()[temp_file].name)
                except:
                    pass
        return jsonify({
            'success': False,
            'error': str(e)
        })

def generate_image_with_gemini(input_image_path, prompt):
    try:
        with open(input_image_path, "rb") as f:
            input_image_data = f.read()

        contents = [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(input_image_data).decode("utf-8"),
                        }
                    },
                ],
            }
        ]

        image_data_chunks = []
        for chunk in model.generate_content_stream(
            contents=contents,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                top_p=1,
                top_k=1,
                max_output_tokens=2048,
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        ):
            if chunk.candidates and chunk.candidates[0].content:
                for part in chunk.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                        image_data_chunks.append(part.inline_data.data)

        if image_data_chunks:
            full_image_data = base64.b64decode(b"".join(image_data_chunks))
            return full_image_data
        else:
            print("No image data found in streamed response.")
            return None

    except Exception as e:
        print(f"Error during Gemini image generation: {e}")
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

        response = requests.post(url, data=payload)

        if response.status_code == 200:
            result = response.json()
            if result['success']:
                image_url = result['data']['url']
                return image_url, None
            else:
                print(f"ImgBB API error: {result.get('error', 'Unknown error from ImgBB')}")
        else:
            print(f"HTTP error uploading to ImgBB: {response.status_code}, body: {response.text}")

        return None, None

    except Exception as e:
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

    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

if __name__ == '__main__':
    print("🚀 Starting Photo Upload QR Generator with Gemini AI Image Generation...")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("🔑 ImgBB API key is hardcoded - ready to go!")
    print("🔑 Make sure your Gemini API key is valid and has image generation access.")
    print("📁 Make sure you have a 'templates' folder with 'index.html'")
    print("🖼️ Place your 'mdc.jpg' logo in a 'static' folder.")

    # Check if templates folder exists
    if not os.path.exists('templates'):
        print("❌ 'templates' folder not found!")
        print("   Create it with: mkdir templates")
        print("   Then save the HTML file as templates/index.html")
    elif not os.path.exists('templates/index.html'):
        print("❌ 'templates/index.html' not found!")
        print("   Save the HTML file as templates/index.html")
    else:
        print("✅ Template files found.")

    if not os.path.exists('static'):
        print("❌ 'static' folder not found!")
        print("   Create it with: mkdir static")
        print("   Place 'mdc.jpg' inside it.")
    elif not os.path.exists('static/mdc.jpg'):
        print("❌ 'static/mdc.jpg' not found!")
        print("   Place your 'mdc.jpg' logo in the 'static' folder.")
    else:
        print("✅ Static files found - starting server...")

    app.run(debug=True, host='0.0.0.0', port=8080)
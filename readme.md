# Bata Figurine Generation with Gemini AI

Take a photo with your device camera or upload from file manager. Uses Google's Gemini AI to generate a shoemaker collectible figurine. Share through QR code link, ImgBB, or Airdrop. Great for printing out!

## Prerequisites

- **Python 3.x**
- **Google Gemini API Key** with image generation access
- **ImgBB API Key** for image hosting

## Setup

Follow these steps to set up and run the application in a virtual environment on a Mac.

### 1. Create a virtual environment

Open your terminal and run the following command to create a virtual environment named `venv`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `config.py` file in the project root with your API keys:

```python
# config.py
GEMINI_API_KEY = "your_gemini_api_key_here"
IMGBB_API_KEY = "your_imgbb_api_key_here"
```

**Getting API Keys:**
- **Gemini API**: Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **ImgBB API**: Get your key from [ImgBB API](https://api.imgbb.com/)

### 3. To run the app

```bash
python app.py
```

The application will be available at: `http://localhost:8080`

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP requests for API calls
- **qrcode**: QR code generation
- **Pillow**: Image processing
- **google-genai**: Google Gemini AI integration

## Usage

1. Start the application with `python app.py`
2. Open your browser to `http://localhost:8080`
3. Either:
   - Click "📁 Upload Photo" to select an image file
   - Click "📹 Start Camera" to take a photo
4. Wait for AI processing (this may take a few moments)
5. View the before/after comparison
6. Use the generated QR code to share your figurine image

## Troubleshooting

- **API Key Issues**: Ensure your `config.py` file exists with valid API keys
- **Camera Access**: Allow camera permissions in your browser
- **Image Upload Fails**: Check file format (supports JPG, PNG, GIF, BMP)
- **AI Generation Fails**: Verify your Gemini API key has image generation access

## License

This project is for internal use by Bata.
# Bata Figurine Generation with Gemini AI

A Flask web application that transforms uploaded photos into collectible figurine images using Google's Gemini AI, then generates QR codes for easy sharing.

## Features

- 📷 **Photo Upload**: Upload images via file picker or camera capture
- 🤖 **AI Transformation**: Convert photos into vintage Bata employee figurines using Gemini AI
- 🔄 **Before/After Comparison**: Toggle between original and generated images
- 📱 **QR Code Generation**: Automatic QR code creation for sharing generated images
- 🌐 **Cloud Storage**: Images hosted on ImgBB for reliable access
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- **Python 3.x**
- **Google Gemini API Key** with image generation access
- **ImgBB API Key** for image hosting
- A virtual environment is highly recommended

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

## Project Structure

```
batamdc-figurine-generation/
├── app.py                 # Main Flask application
├── config.py             # API keys configuration
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main web interface
├── static/
│   └── mdc.jpg          # Company logo
├── favicon/              # Favicon files
│   ├── favicon.ico
│   ├── favicon.svg
│   ├── favicon-96x96.png
│   ├── apple-touch-icon.png
│   └── site.webmanifest
└── README.md
```

## How It Works

1. **Upload**: User uploads a photo via file picker or camera
2. **AI Processing**: Gemini AI transforms the photo into a collectible figurine scene
3. **Hosting**: Generated image is uploaded to ImgBB for permanent hosting
4. **QR Generation**: QR code is created linking to the hosted image
5. **Display**: Before/after comparison panel shows original vs generated image

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
# Photo to QR Generator with Gemini AI

This is a Flask web application that transforms an uploaded photo using the Gemini API, uploads the transformed image to ImgBB, and generates a QR code that links to the new image URL.

## Prerequisites

- **Python 3.x**
- A virtual environment is highly recommended.

## Setup

Follow these steps to set up and run the application in a virtual environment on a Mac.

### 1. Create a virtual environment

Open your terminal and run the following command to create a virtual environment named `venv`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt```
import os
import requests
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure the upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set your remove.bg API credentials
API_URL = "https://api.remove.bg/v1.0/removebg"  # remove.bg API endpoint
API_KEY = "drTXQYDjMxtdju5KQEqCtKKD"  # Your provided API key

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return 'No file uploaded', 400

    file = request.files['photo']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return 'File uploaded successfully'
    else:
        return 'Invalid file type. Only PNG, JPG, and JPEG are allowed.', 400

@app.route('/remove_background', methods=['POST'])
def remove_background():
    # Get the uploaded file
    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        return 'No files to process', 400

    input_path = os.path.join(UPLOAD_FOLDER, files[0])

    # Open the uploaded image and read its content
    with open(input_path, 'rb') as img_file:
        image_data = img_file.read()

    # Prepare the API headers and payload
    headers = {
        "X-Api-Key": API_KEY,  # API key in the header
    }

    files = {
        "image_file": ("image.jpg", image_data)  # Add image data
    }

    # Send the image to the remove.bg API for background removal
    response = requests.post(API_URL, files=files, headers=headers)

    # Check for successful API response
    if response.status_code == 200:
        # Save the result image
        output_path = os.path.join(UPLOAD_FOLDER, 'output.png')
        with open(output_path, 'wb') as out:
            out.write(response.content)

        # Return the image file to the user
        return send_file(output_path, mimetype='image/png')
    else:
        return f"Error: {response.status_code}, {response.text}", 400

if __name__ == '__main__':
    app.run(debug=True)

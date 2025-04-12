from flask import Flask, request, jsonify, redirect, send_from_directory
from flask_cors import CORS
import os
import numpy as np
import cv2
import os
from image_processor import ImageProcessor
from chatbot import FashionChatbot

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize modules
image_processor = ImageProcessor()
chatbot = FashionChatbot()

# Configuration
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Read image file
            img_bytes = file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Process image using ImageProcessor
            body_type = image_processor.detect_body_type(img)
            skin_tone = image_processor.detect_skin_tone(img)
            recommendations = image_processor.generate_recommendations(body_type, skin_tone)
            
            return jsonify({
                'bodyType': body_type,
                'skinTone': skin_tone,
                'recommendations': recommendations
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # Get context from request if available
        context = data.get('context', {})
        
        # Get response from chatbot
        response = chatbot.get_fashion_advice(data['message'], context)
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve frontend files
FRONTEND_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route('/')
def index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)

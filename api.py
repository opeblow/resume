import os
import json
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from src.resume_parser.extraction import extract_text_from_resume, clean_text
from src.resume_parser.parser import parse_resume
from src.resume_parser.question_generator import generate_questions
from src.resume_parser.config import Config

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF and DOCX files are allowed'}), 400
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            raw_text = extract_text_from_resume(tmp_path)
            cleaned_text = clean_text(raw_text)
            parsed_resume = parse_resume(cleaned_text)
            questions = generate_questions(parsed_resume)
            
            result = {
                'parsed_resume': parsed_resume.to_dict(),
                'questions': questions.to_dict()
            }
            return jsonify(result)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    message = data['message']
    resume_context = data.get('resume_context', {})
    conversation_history = data.get('conversation_history', [])
    
    try:
        from src.resume_parser.question_generator import generate_followup_response
        
        response = generate_followup_response(
            message=message,
            resume_context=resume_context,
            conversation_history=conversation_history
        )
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

#
# #Version 2.0.0.0
#
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# import os
# import uuid
# import json
# from datetime import datetime
# from threading import Thread
# import time
# import zipfile
# import requests
#
# app = Flask(__name__)
# CORS(app)  # Enable CORS for frontend integration
# app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
#
# # Configuration
# UPLOAD_FOLDER = 'uploads'
# RESULTS_FOLDER = 'results'
# BATCH_FOLDER = 'batch_processing'
# VARIATIONS_FOLDER = 'variations'
# TRAINING_FOLDER = 'training_originals'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
#
# # COLAB MODEL CONFIGURATION - UPDATE THIS WITH YOUR COLAB URL
# COLAB_MODEL_URL = "https://ede2a3a02d94.ngrok-free.app"  # Replace with your actual Colab URL
#
# # Create necessary directories
# for folder in [UPLOAD_FOLDER, RESULTS_FOLDER, BATCH_FOLDER, VARIATIONS_FOLDER, TRAINING_FOLDER]:
#     os.makedirs(folder, exist_ok=True)
#
# # Global variables
# batch_jobs = {}
#
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# def test_colab_connection():
#     """Test if Colab model is accessible"""
#     try:
#         response = requests.get(f"{COLAB_MODEL_URL}/health", timeout=5)
#         return response.status_code == 200
#     except:
#         return False
#
#
#
# @app.route('/')
# def home():
#     """API documentation"""
#     colab_connected = test_colab_connection()
#
#     return jsonify({
#         "service": "Jharkhand Document Verification API",
#         "version": "1.0",
#         "status": "operational",
#         "deployment": "Local API connected to Colab Model",
#         "colab_model_url": COLAB_MODEL_URL,
#         "colab_connected": colab_connected,
#         "cors_enabled": True,
#         "endpoints": {
#             "single_verification": {
#                 "url": "/verify/single",
#                 "method": "POST",
#                 "description": "Verify a single document via Colab model",
#                 "parameters": "file (multipart/form-data)"
#             },
#             "batch_verification": {
#                 "url": "/verify/batch",
#                 "method": "POST",
#                 "description": "Verify multiple documents via Colab model",
#                 "parameters": "files (multiple files) or zipfile"
#             },
#             "train_model": {
#                 "url": "/train",
#                 "method": "POST",
#                 "description": "Train the ML model via Colab",
#                 "parameters": "files (original documents)"
#             },
#             "generate_variations": {
#                 "url": "/generate/variations",
#                 "method": "POST",
#                 "description": "Generate variations via Colab model",
#                 "parameters": "file (original document), count (optional)"
#             },
#             "batch_status": {
#                 "url": "/batch/status/<job_id>",
#                 "method": "GET",
#                 "description": "Check batch processing status"
#             },
#             "download_results": {
#                 "url": "/download/<job_id>",
#                 "method": "GET",
#                 "description": "Download batch results"
#             },
#             "colab_status": {
#                 "url": "/colab/status",
#                 "method": "GET",
#                 "description": "Check Colab model connection status"
#             }
#         }
#     })
#
#
# # Add preflight OPTIONS handler for CORS
# @app.before_request
# def handle_preflight():
#     if request.method == "OPTIONS":
#         response = jsonify({'status': 'OK'})
#         response.headers.add("Access-Control-Allow-Origin", "*")
#         response.headers.add('Access-Control-Allow-Headers', "*")
#         response.headers.add('Access-Control-Allow-Methods', "*")
#         return response
#
#
# @app.route('/verify/single', methods=['POST', 'OPTIONS'])
# def verify_single_document():
#     """Verify a single document via Colab model"""
#     try:
#         print(f"Received verification request from: {request.remote_addr}")
#
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
#
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
#
#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, TIFF'}), 400
#
#         print(f"Processing file: {file.filename}")
#
#         # Send file to Colab model for prediction
#         try:
#             files = {'file': (file.filename, file.stream, file.content_type)}
#
#             print(f"Sending request to Colab model: {COLAB_MODEL_URL}")
#             response = requests.post(f"{COLAB_MODEL_URL}/predict", files=files, timeout=30)
#
#             if response.status_code == 200:
#                 result = response.json()
#
#                 print(f"Received response from Colab model")
#
#                 return jsonify({
#                     'status': 'success',
#                     'filename': file.filename,
#                     'processed_via': 'colab_model',
#                     'verification_result': {
#                         'document_status': 'AUTHENTIC' if result['is_authentic'] else 'SUSPICIOUS',
#                         'confidence_score': f"{result['confidence']:.1%}",
#                         'detailed_analysis': {
#                             'random_forest_confidence': f"{result['rf_confidence']:.1%}",
#                             'cnn_confidence': f"{result['cnn_confidence']:.1%}",
#                             'combined_confidence': f"{result['confidence']:.1%}"
#                         },
#                         'recommendation': (
#                             'Document appears authentic and can be trusted.'
#                             if result['is_authentic']
#                             else 'Document shows signs of tampering. Manual review recommended.'
#                         ),
#                         'processed_at': datetime.now().isoformat(),
#                         'model_details': result.get('details', {})
#                     },
#                     'security_notice': 'File processed via secure Colab tunnel'
#                 })
#             else:
#                 print(f"Colab model error: {response.status_code} - {response.text}")
#                 return jsonify({
#                     'error': 'Model prediction failed',
#                     'details': f'Colab returned status {response.status_code}',
#                     'colab_response': response.text[:200]  # First 200 chars of error
#                 }), 500
#
#         except requests.exceptions.Timeout:
#             return jsonify({'error': 'Colab model timeout. Please try again.'}), 504
#         except requests.exceptions.ConnectionError:
#             return jsonify({
#                 'error': 'Cannot connect to Colab model',
#                 'solution': 'Make sure your Colab notebook is running and ngrok tunnel is active'
#             }), 503
#
#     except Exception as e:
#         print(f"Error processing file: {str(e)}")
#         return jsonify({'error': f'Processing failed: {str(e)}'}), 500
#
#
# @app.route('/train', methods=['POST', 'OPTIONS'])
# def train_model():
#     """Train the ML model via Colab"""
#     try:
#         print(f"Received training request from: {request.remote_addr}")
#
#         if 'files' not in request.files:
#             return jsonify({'error': 'No files uploaded'}), 400
#
#         files = request.files.getlist('files')
#         if not files:
#             return jsonify({'error': 'No files selected'}), 400
#
#         print(f"Starting training with {len(files)} files via Colab...")
#
#         # Send files to Colab for training
#         try:
#             files_data = []
#             for file in files:
#                 if file and allowed_file(file.filename):
#                     files_data.append(('files', (file.filename, file.stream, file.content_type)))
#
#             variations_per_image = request.form.get('variations_per_image', 100)
#             data = {'variations_per_image': variations_per_image}
#
#             response = requests.post(
#                 f"{COLAB_MODEL_URL}/train",
#                 files=files_data,
#                 data=data,
#                 timeout=300  # 5 minutes timeout for training
#             )
#
#             if response.status_code == 200:
#                 result = response.json()
#                 print("Model training completed via Colab!")
#
#                 return jsonify({
#                     'status': 'success',
#                     'message': 'Model trained successfully via Colab!',
#                     'processed_via': 'colab_model',
#                     'training_results': result.get('training_results', {}),
#                     'trained_at': datetime.now().isoformat(),
#                     'ready_for_verification': True
#                 })
#             else:
#                 return jsonify({
#                     'error': 'Training failed on Colab',
#                     'details': response.text[:200]
#                 }), 500
#
#         except requests.exceptions.Timeout:
#             return jsonify({'error': 'Training timeout. Model training takes time, please wait and check status.'}), 504
#         except requests.exceptions.ConnectionError:
#             return jsonify({
#                 'error': 'Cannot connect to Colab for training',
#                 'solution': 'Ensure Colab notebook is running'
#             }), 503
#
#     except Exception as e:
#         print(f"Training error: {str(e)}")
#         return jsonify({'error': f'Training failed: {str(e)}'}), 500
#
#
# @app.route('/generate/variations', methods=['POST', 'OPTIONS'])
# def generate_document_variations():
#     """Generate variations via Colab model"""
#     try:
#         print(f"Received variation generation request from: {request.remote_addr}")
#
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
#
#         file = request.files['file']
#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type'}), 400
#
#         variation_count = int(request.form.get('count', 100))
#         if variation_count > 200:
#             variation_count = 200
#
#         print(f"Generating {variation_count} variations via Colab...")
#
#         try:
#             files = {'file': (file.filename, file.stream, file.content_type)}
#             data = {'count': variation_count}
#
#             response = requests.post(
#                 f"{COLAB_MODEL_URL}/generate/variations",
#                 files=files,
#                 data=data,
#                 timeout=120
#             )
#
#             if response.status_code == 200:
#                 result = response.json()
#                 print(f"Generated {variation_count} variations successfully via Colab!")
#
#                 return jsonify({
#                     'status': 'success',
#                     'message': f'{variation_count} variations generated successfully via Colab',
#                     'processed_via': 'colab_model',
#                     'original_filename': file.filename,
#                     'variations_generated': result.get('variations_generated', variation_count),
#                     'details': {
#                         'augmentation_methods_used': [
#                             'noise_addition', 'grayscale_conversion', 'dark_spots',
#                             'ink_blur', 'brightness_adjustment', 'rotation',
#                             'perspective_distortion', 'scan_lines', 'paper_texture'
#                         ],
#                         'ready_for_training': True,
#                         'generated_at': datetime.now().isoformat()
#                     }
#                 })
#             else:
#                 return jsonify({
#                     'error': 'Variation generation failed on Colab',
#                     'details': response.text[:200]
#                 }), 500
#
#         except requests.exceptions.Timeout:
#             return jsonify({'error': 'Variation generation timeout'}), 504
#         except requests.exceptions.ConnectionError:
#             return jsonify({'error': 'Cannot connect to Colab for variation generation'}), 503
#
#     except Exception as e:
#         print(f"Variation generation error: {str(e)}")
#         return jsonify({'error': f'Variation generation failed: {str(e)}'}), 500
#
#
# @app.route('/verify/batch', methods=['POST', 'OPTIONS'])
# def verify_batch_documents():
#     """Verify multiple documents via Colab model"""
#     try:
#         print(f"Received batch verification request from: {request.remote_addr}")
#
#         job_id = str(uuid.uuid4())
#         job_folder = os.path.join(BATCH_FOLDER, job_id)
#         os.makedirs(job_folder, exist_ok=True)
#
#         files_to_process = []
#
#         # Handle ZIP file upload
#         if 'zipfile' in request.files:
#             zip_file = request.files['zipfile']
#             if zip_file.filename.endswith('.zip'):
#                 zip_path = os.path.join(job_folder, 'upload.zip')
#                 zip_file.save(zip_path)
#                 with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                     zip_ref.extractall(job_folder)
#                 for root, dirs, files in os.walk(job_folder):
#                     for file in files:
#                         if allowed_file(file):
#                             files_to_process.append(os.path.join(root, file))
#
#         # Handle multiple file upload
#         elif 'files' in request.files:
#             files = request.files.getlist('files')
#             for file in files:
#                 if file and allowed_file(file.filename):
#                     filename = secure_filename(file.filename)
#                     file_path = os.path.join(job_folder, filename)
#                     file.save(file_path)
#                     files_to_process.append(file_path)
#
#         if not files_to_process:
#             return jsonify({'error': 'No valid image files found'}), 400
#
#         # Initialize batch job
#         batch_jobs[job_id] = {
#             'status': 'processing',
#             'total_files': len(files_to_process),
#             'processed_files': 0,
#             'results': [],
#             'started_at': datetime.now().isoformat(),
#             'completed_at': None
#         }
#
#         # Start background processing
#         thread = Thread(target=process_batch_job, args=(job_id, files_to_process))
#         thread.start()
#
#         print(f"Started batch job {job_id} with {len(files_to_process)} files")
#
#         return jsonify({
#             'status': 'success',
#             'message': 'Batch processing started via Colab model',
#             'job_id': job_id,
#             'total_files': len(files_to_process),
#             'status_url': f'/batch/status/{job_id}',
#             'estimated_time': f'{len(files_to_process) * 5} seconds',
#             'processed_via': 'colab_model'
#         })
#     except Exception as e:
#         print(f"Batch processing error: {str(e)}")
#         return jsonify({'error': f'Batch processing failed: {str(e)}'}), 500
#
#
# def process_batch_job(job_id, files_to_process):
#     """Background function to process batch jobs via Colab model"""
#     try:
#         results = []
#         print(f"Processing batch job {job_id} via Colab...")
#
#         for i, file_path in enumerate(files_to_process):
#             try:
#                 # Send file to Colab model
#                 with open(file_path, 'rb') as f:
#                     files = {'file': (os.path.basename(file_path), f, 'image/jpeg')}
#                     response = requests.post(f"{COLAB_MODEL_URL}/predict", files=files, timeout=30)
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     file_result = {
#                         'filename': os.path.basename(file_path),
#                         'status': 'processed',
#                         'is_authentic': result['is_authentic'],
#                         'confidence': f"{result['confidence']:.1%}",
#                         'verdict': 'AUTHENTIC' if result['is_authentic'] else 'SUSPICIOUS',
#                         'rf_confidence': f"{result['rf_confidence']:.1%}",
#                         'cnn_confidence': f"{result['cnn_confidence']:.1%}",
#                         'details': result.get('details', {})
#                     }
#                 else:
#                     file_result = {
#                         'filename': os.path.basename(file_path),
#                         'status': 'error',
#                         'error': f'Colab model error: {response.status_code}'
#                     }
#
#                 results.append(file_result)
#                 batch_jobs[job_id]['processed_files'] = i + 1
#                 batch_jobs[job_id]['results'] = results
#
#                 print(f"Processed {i + 1}/{len(files_to_process)} files")
#                 time.sleep(0.5)  # Prevent overwhelming Colab
#
#             except Exception as e:
#                 print(f"Error processing file {os.path.basename(file_path)}: {str(e)}")
#                 results.append({
#                     'filename': os.path.basename(file_path),
#                     'status': 'error',
#                     'error': str(e)
#                 })
#
#         # Mark job as completed
#         batch_jobs[job_id]['status'] = 'completed'
#         batch_jobs[job_id]['completed_at'] = datetime.now().isoformat()
#
#         # Generate summary report
#         authentic_count = sum(1 for r in results if r.get('is_authentic', False))
#         suspicious_count = len(
#             [r for r in results if not r.get('is_authentic', True) and r.get('status') == 'processed'])
#         batch_jobs[job_id]['summary'] = {
#             'total_processed': len(results),
#             'authentic_documents': authentic_count,
#             'suspicious_documents': suspicious_count,
#             'success_rate': f"{(authentic_count / len(results) * 100):.1f}%" if results else "0%"
#         }
#
#         print(f"Batch job {job_id} completed successfully via Colab!")
#
#     except Exception as e:
#         print(f"Batch job {job_id} failed: {str(e)}")
#         batch_jobs[job_id]['status'] = 'failed'
#         batch_jobs[job_id]['error'] = str(e)
#
#
# @app.route('/colab/status', methods=['GET'])
# def colab_status():
#     """Check Colab model connection status"""
#     connected = test_colab_connection()
#
#     return jsonify({
#         'colab_url': COLAB_MODEL_URL,
#         'connected': connected,
#         'status': 'online' if connected else 'offline',
#         'last_checked': datetime.now().isoformat(),
#         'message': 'Colab model is accessible' if connected else 'Cannot reach Colab model. Check if notebook is running.'
#     })
#
#
# @app.route('/batch/status/<job_id>', methods=['GET'])
# def get_batch_status(job_id):
#     """Get batch processing status"""
#     if job_id not in batch_jobs:
#         return jsonify({'error': 'Job not found'}), 404
#
#     job = batch_jobs[job_id]
#     response = {
#         'job_id': job_id,
#         'status': job['status'],
#         'progress': {
#             'total_files': job['total_files'],
#             'processed_files': job['processed_files'],
#             'percentage': f"{(job['processed_files'] / job['total_files'] * 100):.1f}%"
#         },
#         'started_at': job['started_at']
#     }
#
#     if job['status'] == 'completed':
#         response['completed_at'] = job['completed_at']
#         response['summary'] = job['summary']
#         response['download_url'] = f'/download/{job_id}'
#         response['results'] = job['results']
#     elif job['status'] == 'failed':
#         response['error'] = job.get('error', 'Unknown error')
#
#     return jsonify(response)
#
#
# @app.route('/download/<job_id>', methods=['GET'])
# def download_batch_results(job_id):
#     """Download batch processing results"""
#     if job_id not in batch_jobs or batch_jobs[job_id]['status'] != 'completed':
#         return jsonify({'error': 'Results not available'}), 404
#
#     report = {
#         'job_id': job_id,
#         'processing_summary': batch_jobs[job_id]['summary'],
#         'detailed_results': batch_jobs[job_id]['results'],
#         'processed_at': batch_jobs[job_id]['completed_at']
#     }
#
#     report_path = os.path.join(BATCH_FOLDER, job_id, 'verification_report.json')
#     with open(report_path, 'w') as f:
#         json.dump(report, f, indent=2)
#
#     return send_from_directory(
#         os.path.join(BATCH_FOLDER, job_id),
#         'verification_report.json',
#         as_attachment=True,
#         download_name=f'verification_report_{job_id}.json'
#     )
#
#
# @app.route('/health', methods=['GET'])
# def health_check():
#     """API health check"""
#     colab_connected = test_colab_connection()
#
#     return jsonify({
#         'status': 'healthy',
#         'service': 'Document Verification API',
#         'deployment': 'local_api_with_colab_model',
#         'timestamp': datetime.now().isoformat(),
#         'colab_model_connected': colab_connected,
#         'cors_enabled': True
#     })
#
#
# # Enhanced error handlers
# @app.errorhandler(413)
# def too_large(e):
#     return jsonify({
#         'error': 'File too large. Maximum size: 50MB',
#         'max_size': '50MB'
#     }), 413
#
#
# @app.errorhandler(404)
# def not_found(e):
#     return jsonify({
#         'error': 'Endpoint not found',
#         'available_endpoints': [
#             '/', '/verify/single', '/train', '/generate/variations',
#             '/verify/batch', '/health', '/colab/status'
#         ]
#     }), 404
#
#
# @app.errorhandler(500)
# def internal_error(e):
#     print(f"Internal server error: {str(e)}")
#     return jsonify({'error': 'Internal server error'}), 500
#
#
# if __name__ == '__main__':
#     print("=" * 60)
#     print("Starting Jharkhand Document Verification API")
#     print("=" * 60)
#
#     print(f"Colab Model URL: {COLAB_MODEL_URL}")
#
#     # Test Colab connection
#     if test_colab_connection():
#         print("✅ Colab model connection successful!")
#     else:
#         print("⚠️  Cannot connect to Colab model")
#         print("   Make sure:")
#         print("   1. Colab notebook is running")
#         print("   2. ngrok tunnel is active in Colab")
#         print("   3. Update COLAB_MODEL_URL with correct ngrok URL")
#
#     print("\nAPI Endpoints:")
#     print("   Single Verification: POST /verify/single")
#     print("   Batch Verification:  POST /verify/batch")
#     print("   Train Model:         POST /train")
#     print("   Generate Variations: POST /generate/variations")
#     print("   Batch Status:        GET /batch/status/<job_id>")
#     print("   Download Results:    GET /download/<job_id>")
#     print("   Colab Status:        GET /colab/status")
#     print("   Health Check:        GET /health")
#     print("   Documentation:       GET /")
#
#     print(f"\nServer Details:")
#     print(f"   Local URL:  http://localhost:5000")
#     print(f"   Host:       0.0.0.0")
#     print(f"   Port:       5000")
#     print(f"   CORS:       Enabled")
#     print(f"   Max Upload: 50MB")
#
#     print(f"\nngrok Setup:")
#     print(f"   1. Open new terminal")
#     print(f"   2. Run: ngrok http 5000")
#     print(f"   3. Copy the https:// URL")
#     print(f"   4. Use that URL in your HTML files")
#
#     print("\n" + "=" * 60)
#     print("Starting Flask server...")
#     print("=" * 60)
#
#     # Run Flask app
#     app.run(
#         debug=False,
#         host='0.0.0.0',
#         port=5000,
#         threaded=True
#     )

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
from threading import Thread
import time
import zipfile
import requests
import re
import logging
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
BATCH_FOLDER = 'batch_processing'
VARIATIONS_FOLDER = 'variations'
TRAINING_FOLDER = 'training_originals'
LOGS_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# API Keys and URLs
COLAB_MODEL_URL = "https://c5e4469cc430.ngrok-free.app"  # Your Colab URL
OCR_SPACE_API_KEY = "K87686939788957"  # Replace with your OCR.space API key

# Supabase Configuration
SUPABASE_URL = "https://kwztlhywsczfajjtpjmo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt3enRsaHl3c2N6ZmFqanRwam1vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcxNzk5NjMsImV4cCI6MjA3Mjc1NTk2M30.vjr315rV_HkZkVVpPmhqc4eNgWKcRLowOf_8-osH1KU"
SUPABASE_TABLE = "Student_Data"

###


supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

###
# Create necessary directories
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER, BATCH_FOLDER, VARIATIONS_FOLDER, TRAINING_FOLDER, LOGS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_FOLDER, 'verification.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variables
batch_jobs = {}


class VerificationLogger:
    """Class for logging verification attempts and flagged users"""

    def __init__(self, logs_folder):
        self.logs_folder = logs_folder
        self.flagged_users_file = os.path.join(logs_folder, 'flagged_users.json')
        self.verification_log_file = os.path.join(logs_folder, 'verification_attempts.json')

        # Initialize log files if they don't exist
        for file_path in [self.flagged_users_file, self.verification_log_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)

    def log_verification_attempt(self, attempt_data):
        """Log every verification attempt"""
        try:
            # Read existing logs
            with open(self.verification_log_file, 'r') as f:
                logs = json.load(f)

            # Add new attempt
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'attempt_id': str(uuid.uuid4()),
                **attempt_data
            })

            # Keep only last 10000 records to prevent file from growing too large
            if len(logs) > 10000:
                logs = logs[-10000:]

            # Write back
            with open(self.verification_log_file, 'w') as f:
                json.dump(logs, f, indent=2)

            logger.info(f"Logged verification attempt: {attempt_data.get('status', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to log verification attempt: {str(e)}")

    def flag_user(self, flag_data):
        """Flag suspicious users and log their details"""
        try:
            # Read existing flagged users
            with open(self.flagged_users_file, 'r') as f:
                flagged_users = json.load(f)

            # Add new flagged user
            flagged_entry = {
                'flag_id': str(uuid.uuid4()),
                'flagged_at': datetime.now().isoformat(),
                'ip_address': flag_data.get('ip_address'),
                'filename': flag_data.get('filename'),
                'extracted_data': flag_data.get('extracted_data', {}),
                'flag_reason': flag_data.get('flag_reason'),
                'validation_details': flag_data.get('validation_details', {}),
                'severity': flag_data.get('severity', 'medium')  # low, medium, high
            }

            flagged_users.append(flagged_entry)

            # Write back
            with open(self.flagged_users_file, 'w') as f:
                json.dump(flagged_users, f, indent=2)

            logger.warning(
                f"USER FLAGGED: {flag_data.get('flag_reason')} - MS No: {flag_data.get('extracted_data', {}).get('ms_no', 'N/A')}")

            return flagged_entry['flag_id']

        except Exception as e:
            logger.error(f"Failed to flag user: {str(e)}")
            return None

    def get_flagged_users_summary(self):
        """Get summary of flagged users"""
        try:
            with open(self.flagged_users_file, 'r') as f:
                flagged_users = json.load(f)

            return {
                'total_flagged': len(flagged_users),
                'flagged_today': len(
                    [u for u in flagged_users if u['flagged_at'].startswith(datetime.now().strftime('%Y-%m-%d'))]),
                'recent_flags': flagged_users[-5:] if flagged_users else []
            }
        except:
            return {'total_flagged': 0, 'flagged_today': 0, 'recent_flags': []}


class MarksheetOCR:
    """OCR class for extracting marksheet data"""

    def __init__(self, api_key):
        self.api_key = api_key

    def extract_text_from_image(self, image_path):
        """Extract text using OCR.space API"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'apikey': self.api_key,
                    'language': 'eng',
                    'isOverlayRequired': False,
                    'isCreateSearchablePdf': False,
                    'isSearchablePdfHideTextLayer': False,
                    'scale': True,
                    'isTable': True
                }

                response = requests.post(
                    'https://api.ocr.space/parse/image',
                    files=files,
                    data=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('IsErroredOnProcessing'):
                        return None, f"OCR Error: {result.get('ErrorMessage', 'Unknown error')}"

                    extracted_text = ""
                    for parsed_result in result.get('ParsedResults', []):
                        extracted_text += parsed_result.get('ParsedText', '')

                    return extracted_text, None
                else:
                    return None, f"OCR API Error: {response.status_code}"

        except Exception as e:
            return None, f"OCR Exception: {str(e)}"

    def parse_marksheet_data(self, extracted_text):
        """Parse extracted text to find key marksheet information"""
        data = {
            'ms_no': None,
            'name': None,
            'college': None,
            'total_marks': None,
            'roll_code': None,
            'roll_no': None,
            'registration_no': None
        }

        # Clean up text
        text_lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        full_text = ' '.join(text_lines)

        # Extract M.S No (various patterns)
        ms_patterns = [
            r'M\.S\s*No\.?\s*:?\s*(\d+)',
            r'MS\s*No\.?\s*:?\s*(\d+)',
            r'M\.S\s*Number\s*:?\s*(\d+)',
            r'Mark\s*Sheet\s*No\.?\s*:?\s*(\d+)'
        ]

        for pattern in ms_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                data['ms_no'] = int(match.group(1))
                break

        # Extract Name (look for patterns like "Name: John Doe" or "Student Name: John Doe")
        name_patterns = [
            r'Name\s*:?\s*([A-Za-z\s]+?)(?=\s*(?:Roll|M\.S|College|Father|Mother|$))',
            r'Student\s*Name\s*:?\s*([A-Za-z\s]+?)(?=\s*(?:Roll|M\.S|College|Father|Mother|$))',
            r'Candidate\s*Name\s*:?\s*([A-Za-z\s]+?)(?=\s*(?:Roll|M\.S|College|Father|Mother|$))'
        ]

        for pattern in name_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and not name.isdigit():  # Basic validation
                    data['name'] = name
                    break

        # Extract College name
        college_patterns = [
            r'College\s*:?\s*([^:\n]+?)(?=\s*(?:Roll|M\.S|Name|$))',
            r'Institution\s*:?\s*([^:\n]+?)(?=\s*(?:Roll|M\.S|Name|$))',
            r'([A-Za-z\s,]+College[A-Za-z\s,]*)',
            r'([A-Za-z\s,]+Institute[A-Za-z\s,]*)'
        ]

        for pattern in college_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                college = match.group(1).strip()
                if len(college) > 5:  # Basic validation
                    data['college'] = college
                    break

        # Extract Total Marks
        total_patterns = [
            r'Total\s*:?\s*(\d+)',
            r'Grand\s*Total\s*:?\s*(\d+)',
            r'Overall\s*Total\s*:?\s*(\d+)',
            r'Total\s*Marks\s*:?\s*(\d+)'
        ]

        for pattern in total_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                data['total_marks'] = int(match.group(1))
                break

        # Extract Roll Code and Roll No
        roll_patterns = [
            r'Roll\s*Code\s*:?\s*(\d+)',
            r'Roll\s*No\.?\s*:?\s*(\d+)'
        ]

        roll_matches = re.findall(r'Roll\s*(?:Code|No\.?)\s*:?\s*(\d+)', full_text, re.IGNORECASE)
        if len(roll_matches) >= 2:
            data['roll_code'] = int(roll_matches[0])
            data['roll_no'] = int(roll_matches[1])
        elif len(roll_matches) == 1:
            data['roll_no'] = int(roll_matches[0])

        # Extract Registration No
        reg_patterns = [
            r'Registration\s*No\.?\s*:?\s*([A-Za-z0-9]+)',
            r'Reg\.?\s*No\.?\s*:?\s*([A-Za-z0-9]+)',
            r'Registration\s*Number\s*:?\s*([A-Za-z0-9]+)'
        ]

        for pattern in reg_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                data['registration_no'] = match.group(1).strip()
                break

        return data


class DatabaseValidator:
    """Class for validating marksheet data against Supabase database using direct HTTP requests"""

    def __init__(self, supabase_url, supabase_key):
        self.base_url = f"{supabase_url}/rest/v1"
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }

    def validate_marksheet(self, extracted_data, request_info=None):
        """Validate extracted data against database with comprehensive flagging"""
        try:
            # Primary validation using M.S No
            if not extracted_data.get('ms_no'):
                # FLAG: No MS No found
                flag_data = {
                    'ip_address': request_info.get('ip') if request_info else None,
                    'filename': request_info.get('filename') if request_info else None,
                    'extracted_data': extracted_data,
                    'flag_reason': 'MS_NO_NOT_FOUND_IN_OCR',
                    'severity': 'high'
                }
                flag_id = verification_logger.flag_user(flag_data)

                return {
                    'is_valid': False,
                    'error': 'M.S No not found in marksheet',
                    'confidence': 0.0,
                    'flag_id': flag_id
                }

            # Make direct HTTP request to Supabase
            # Make direct HTTP request to Supabase
            url = f"{self.base_url}/{SUPABASE_TABLE}"
            params = {'"M.S No"': f"eq.{extracted_data['ms_no']}"}  # Escaped column name with quotes
            response = requests.get(url, headers=self.headers, params=params)
            ##temporaryy code hai
            print(f"=== DATABASE QUERY DEBUG ===")
            print(f"URL: {url}")
            print(f"Params: {params}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print("=== END DEBUG ===")
            ##

            if response.status_code != 200:
                # FLAG: Database query failed
                flag_data = {
                    'ip_address': request_info.get('ip') if request_info else None,
                    'filename': request_info.get('filename') if request_info else None,
                    'extracted_data': extracted_data,
                    'flag_reason': 'DATABASE_QUERY_ERROR',
                    'validation_details': {
                        'http_status': response.status_code,
                        'response_text': response.text
                    },
                    'severity': 'high'
                }
                flag_id = verification_logger.flag_user(flag_data)

                return {
                    'is_valid': False,
                    'error': f'Database query failed: HTTP {response.status_code}',
                    'confidence': 0.0,
                    'flag_id': flag_id
                }

            result_data = response.json()

            if not result_data:
                # FLAG: MS No not found in database
                flag_data = {
                    'ip_address': request_info.get('ip') if request_info else None,
                    'filename': request_info.get('filename') if request_info else None,
                    'extracted_data': extracted_data,
                    'flag_reason': 'MS_NO_NOT_IN_DATABASE',
                    'validation_details': {'searched_ms_no': extracted_data['ms_no']},
                    'severity': 'high'
                }
                flag_id = verification_logger.flag_user(flag_data)

                return {
                    'is_valid': False,
                    'error': 'M.S No not found in database',
                    'confidence': 0.0,
                    'extracted_ms_no': extracted_data.get('ms_no'),
                    'flag_id': flag_id
                }

            # Found matching record - now validate required fields (2 out of 3 must match)
            db_record = result_data[0]
            validation_results = {}
            passed_required_checks = 0
            total_required_checks = 0
            validation_issues = []

            # Required Field 1: Validate M.S No (already matched - exact match)
            validation_results['ms_no_match'] = {
                'exact_match': True,
                'extracted': extracted_data['ms_no'],
                'database': db_record.get('M.S No')
            }
            passed_required_checks += 1
            total_required_checks += 1

            # Required Field 2: Validate Name (fuzzy match)
            if extracted_data.get('name') and db_record.get('Name'):
                extracted_name = extracted_data['name'].strip().upper()
                db_name = db_record['Name'].strip().upper()
                name_match_score = self._fuzzy_match(extracted_name, db_name)
                name_passed = name_match_score >= 0.7

                validation_results['name_match'] = {
                    'score': name_match_score,
                    'passed': name_passed,
                    'extracted': extracted_data['name'],
                    'database': db_record['Name']
                }

                if name_passed:
                    passed_required_checks += 1
                else:
                    validation_issues.append(
                        f"Name mismatch: OCR='{extracted_data['name']}' vs DB='{db_record['Name']}' (score: {name_match_score:.2f})")
                total_required_checks += 1
            else:
                validation_issues.append("Name not found in OCR extraction or database")
                validation_results['name_match'] = {
                    'score': 0.0,
                    'passed': False,
                    'extracted': extracted_data.get('name'),
                    'database': db_record.get('Name')
                }
                total_required_checks += 1

            # Required Field 3: Validate Roll No (fuzzy match)
            if extracted_data.get('roll_no') and db_record.get('Roll No'):
                extracted_roll = str(extracted_data['roll_no']).strip().upper()
                db_roll = str(db_record['Roll No']).strip().upper()
                roll_match_score = self._fuzzy_match(extracted_roll, db_roll)
                roll_passed = roll_match_score >= 0.7

                validation_results['roll_no_match'] = {
                    'score': roll_match_score,
                    'passed': roll_passed,
                    'extracted': extracted_data['roll_no'],
                    'database': db_record['Roll No']
                }

                if roll_passed:
                    passed_required_checks += 1
                else:
                    validation_issues.append(
                        f"Roll No mismatch: OCR='{extracted_data['roll_no']}' vs DB='{db_record['Roll No']}' (score: {roll_match_score:.2f})")
                total_required_checks += 1
            else:
                validation_issues.append("Roll No not found in OCR extraction or database")
                validation_results['roll_no_match'] = {
                    'score': 0.0,
                    'passed': False,
                    'extracted': extracted_data.get('roll_no'),
                    'database': db_record.get('Roll No')
                }
                total_required_checks += 1

            # Optional Field: Validate Total Marks (doesn't affect pass/fail)
            if extracted_data.get('total_marks') and db_record.get('Total'):
                marks_match = extracted_data['total_marks'] == db_record['Total']
                validation_results['total_marks_match'] = {
                    'exact_match': marks_match,
                    'extracted': extracted_data['total_marks'],
                    'database': db_record['Total']
                }

                if not marks_match:
                    # Log mismatch but don't add to validation issues (it's optional)
                    validation_results['total_marks_match'][
                        'note'] = "Optional field - mismatch logged but doesn't affect validation"
            else:
                validation_results['total_marks_match'] = {
                    'exact_match': None,
                    'extracted': extracted_data.get('total_marks'),
                    'database': db_record.get('Total'),
                    'note': "Optional field - not available for comparison"
                }

            # Calculate validation success (2 out of 3 required fields must pass)
            required_fields_passed = passed_required_checks >= 2
            confidence_score = passed_required_checks / total_required_checks if total_required_checks > 0 else 0

            # Flag user if validation fails or confidence is very low
            flag_id = None
            if not required_fields_passed:
                flag_reason = "INSUFFICIENT_REQUIRED_FIELD_MATCHES"
                severity = 'high'
            elif confidence_score < 0.5:  # Less than 50% of fields match
                flag_reason = "LOW_VALIDATION_CONFIDENCE"
                severity = 'medium'
            else:
                flag_reason = None

            if flag_reason:
                flag_data = {
                    'ip_address': request_info.get('ip') if request_info else None,
                    'filename': request_info.get('filename') if request_info else None,
                    'extracted_data': extracted_data,
                    'flag_reason': flag_reason,
                    'validation_details': {
                        'validation_results': validation_results,
                        'validation_issues': validation_issues,
                        'passed_required_checks': passed_required_checks,
                        'total_required_checks': total_required_checks,
                        'confidence_score': confidence_score,
                        'database_record_ms_no': db_record.get('M.S No')
                    },
                    'severity': severity
                }
                flag_id = verification_logger.flag_user(flag_data)

            return {
                'is_valid': required_fields_passed,
                'confidence': confidence_score,
                'validation_details': validation_results,
                'validation_issues': validation_issues,
                'database_record': db_record,
                'extracted_data': extracted_data,
                'total_checks': total_required_checks,
                'passed_checks': passed_required_checks,
                'required_fields_passed': required_fields_passed,
                'flag_id': flag_id
            }

        except Exception as e:
            # FLAG: Database validation error
            flag_data = {
                'ip_address': request_info.get('ip') if request_info else None,
                'filename': request_info.get('filename') if request_info else None,
                'extracted_data': extracted_data,
                'flag_reason': 'DATABASE_VALIDATION_ERROR',
                'validation_details': {'error': str(e)},
                'severity': 'medium'
            }
            flag_id = verification_logger.flag_user(flag_data)

            return {
                'is_valid': False,
                'error': f'Database validation error: {str(e)}',
                'confidence': 0.0,
                'flag_id': flag_id
            }

    def _fuzzy_match(self, str1, str2):
        """Simple fuzzy matching using Levenshtein-like approach"""
        if not str1 or not str2:
            return 0.0

        # Simple approach - check for common words and character similarity
        words1 = set(str1.split())
        words2 = set(str2.split())

        if not words1 or not words2:
            return 0.0

        common_words = words1.intersection(words2)
        union_words = words1.union(words2)

        return len(common_words) / len(union_words) if union_words else 0.0


# Initialize components (FIXED: Proper initialization order)
verification_logger = VerificationLogger(LOGS_FOLDER)
db_validator = DatabaseValidator(SUPABASE_URL, SUPABASE_KEY)

# Debug: Test HTTP connection to Supabase (FIXED: Using direct HTTP)
print("=== SUPABASE HTTP CLIENT DEBUG ===")
print(f"URL: {SUPABASE_URL}")
print(f"Key exists: {SUPABASE_KEY is not None}")
print(f"Key length: {len(SUPABASE_KEY) if SUPABASE_KEY else 0}")
print(f"Key first 10 chars: {SUPABASE_KEY[:10] if SUPABASE_KEY else 'None'}")

# Test HTTP connection immediately
try:
    test_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    test_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    test_params = {"select": "*", "limit": "1"}

    response = requests.get(test_url, headers=test_headers, params=test_params, timeout=10)
    print(f"HTTP Status: {response.status_code}")
    if response.status_code == 200:
        print("HTTP Connection test: SUCCESS")
        result = response.json()
        print(f"Sample data count: {len(result)}")
    else:
        print(f"HTTP Connection test: FAILED - {response.text}")
except Exception as e:
    print(f"HTTP Connection test: FAILED - {e}")
print("=== END DEBUG ===")


# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']


# Initialize OCR
ocr_processor = MarksheetOCR(OCR_SPACE_API_KEY)


# Your Flask routes would go here...
def validate_marksheet(self, extracted_data, request_info=None):
    """Validate extracted data against database with comprehensive flagging"""
    try:
        # Build query based on available data
        query = self.supabase.table(SUPABASE_TABLE).select("*")

        # Primary validation using M.S No
        if not extracted_data.get('ms_no'):
            # FLAG: No MS No found
            flag_data = {
                'ip_address': request_info.get('ip') if request_info else None,
                'filename': request_info.get('filename') if request_info else None,
                'extracted_data': extracted_data,
                'flag_reason': 'MS_NO_NOT_FOUND_IN_OCR',
                'severity': 'high'
            }
            verification_logger.flag_user(flag_data)

            return {
                'is_valid': False,
                'error': 'M.S No not found in marksheet',
                'confidence': 0.0,
                'flag_id': verification_logger.flag_user(flag_data)
            }

        query = query.eq('M.S No', extracted_data['ms_no'])
        result = query.execute()

        if not result.data:
            # FLAG: MS No not found in database
            flag_data = {
                'ip_address': request_info.get('ip') if request_info else None,
                'filename': request_info.get('filename') if request_info else None,
                'extracted_data': extracted_data,
                'flag_reason': 'MS_NO_NOT_IN_DATABASE',
                'validation_details': {'searched_ms_no': extracted_data['ms_no']},
                'severity': 'high'
            }
            flag_id = verification_logger.flag_user(flag_data)

            return {
                'is_valid': False,
                'error': 'M.S No not found in database',
                'confidence': 0.0,
                'extracted_ms_no': extracted_data.get('ms_no'),
                'flag_id': flag_id
            }

        # Found matching record - now validate required fields (2 out of 3 must match)
        db_record = result.data[0]
        validation_results = {}
        passed_required_checks = 0
        total_required_checks = 0
        validation_issues = []

        # Required Field 1: Validate M.S No (already matched - exact match)
        validation_results['ms_no_match'] = {
            'exact_match': True,
            'extracted': extracted_data['ms_no'],
            'database': db_record.get('M.S No')
        }
        passed_required_checks += 1
        total_required_checks += 1

        # Required Field 2: Validate Name (fuzzy match)
        if extracted_data.get('name') and db_record.get('Name'):
            extracted_name = extracted_data['name'].strip().upper()
            db_name = db_record['Name'].strip().upper()
            name_match_score = self._fuzzy_match(extracted_name, db_name)
            name_passed = name_match_score >= 0.7

            validation_results['name_match'] = {
                'score': name_match_score,
                'passed': name_passed,
                'extracted': extracted_data['name'],
                'database': db_record['Name']
            }

            if name_passed:
                passed_required_checks += 1
            else:
                validation_issues.append(
                    f"Name mismatch: OCR='{extracted_data['name']}' vs DB='{db_record['Name']}' (score: {name_match_score:.2f})")
            total_required_checks += 1
        else:
            validation_issues.append("Name not found in OCR extraction or database")
            validation_results['name_match'] = {
                'score': 0.0,
                'passed': False,
                'extracted': extracted_data.get('name'),
                'database': db_record.get('Name')
            }
            total_required_checks += 1

        # Required Field 3: Validate Roll No (fuzzy match)
        if extracted_data.get('roll_no') and db_record.get('Roll No'):
            extracted_roll = str(extracted_data['roll_no']).strip().upper()
            db_roll = str(db_record['Roll No']).strip().upper()
            roll_match_score = self._fuzzy_match(extracted_roll, db_roll)
            roll_passed = roll_match_score >= 0.7

            validation_results['roll_no_match'] = {
                'score': roll_match_score,
                'passed': roll_passed,
                'extracted': extracted_data['roll_no'],
                'database': db_record['Roll No']
            }

            if roll_passed:
                passed_required_checks += 1
            else:
                validation_issues.append(
                    f"Roll No mismatch: OCR='{extracted_data['roll_no']}' vs DB='{db_record['Roll No']}' (score: {roll_match_score:.2f})")
            total_required_checks += 1
        else:
            validation_issues.append("Roll No not found in OCR extraction or database")
            validation_results['roll_no_match'] = {
                'score': 0.0,
                'passed': False,
                'extracted': extracted_data.get('roll_no'),
                'database': db_record.get('Roll No')
            }
            total_required_checks += 1

        # Optional Field: Validate Total Marks (doesn't affect pass/fail)
        if extracted_data.get('total_marks') and db_record.get('Total'):
            marks_match = extracted_data['total_marks'] == db_record['Total']
            validation_results['total_marks_match'] = {
                'exact_match': marks_match,
                'extracted': extracted_data['total_marks'],
                'database': db_record['Total']
            }

            if not marks_match:
                # Log mismatch but don't add to validation issues (it's optional)
                validation_results['total_marks_match'][
                    'note'] = "Optional field - mismatch logged but doesn't affect validation"
        else:
            validation_results['total_marks_match'] = {
                'exact_match': None,
                'extracted': extracted_data.get('total_marks'),
                'database': db_record.get('Total'),
                'note': "Optional field - not available for comparison"
            }

        # Calculate validation success (2 out of 3 required fields must pass)
        required_fields_passed = passed_required_checks >= 2
        confidence_score = passed_required_checks / total_required_checks if total_required_checks > 0 else 0

        # Flag user if validation fails or confidence is very low
        flag_id = None
        if not required_fields_passed:
            flag_reason = "INSUFFICIENT_REQUIRED_FIELD_MATCHES"
            severity = 'high'
        elif confidence_score < 0.5:  # Less than 50% of fields match
            flag_reason = "LOW_VALIDATION_CONFIDENCE"
            severity = 'medium'
        else:
            flag_reason = None

        if flag_reason:
            flag_data = {
                'ip_address': request_info.get('ip') if request_info else None,
                'filename': request_info.get('filename') if request_info else None,
                'extracted_data': extracted_data,
                'flag_reason': flag_reason,
                'validation_details': {
                    'validation_results': validation_results,
                    'validation_issues': validation_issues,
                    'passed_required_checks': passed_required_checks,
                    'total_required_checks': total_required_checks,
                    'confidence_score': confidence_score,
                    'database_record_ms_no': db_record.get('M.S No')
                },
                'severity': severity
            }
            flag_id = verification_logger.flag_user(flag_data)

        return {
            'is_valid': required_fields_passed,
            'confidence': confidence_score,
            'validation_details': validation_results,
            'validation_issues': validation_issues,
            'database_record': db_record,
            'extracted_data': extracted_data,
            'total_checks': total_required_checks,
            'passed_checks': passed_required_checks,
            'required_fields_passed': required_fields_passed,
            'flag_id': flag_id
        }

    except Exception as e:
        # FLAG: Database validation error
        flag_data = {
            'ip_address': request_info.get('ip') if request_info else None,
            'filename': request_info.get('filename') if request_info else None,
            'extracted_data': extracted_data,
            'flag_reason': 'DATABASE_VALIDATION_ERROR',
            'validation_details': {'error': str(e)},
            'severity': 'medium'
        }
        flag_id = verification_logger.flag_user(flag_data)

        #
        # Add this debug logging before returning results
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Validation Debug - MS No: {extracted_data.get('ms_no')}")
        logger.info(f"Required fields passed: {passed_required_checks}/3")
        logger.info(f"Validation details: {validation_results}")
        logger.info(f"Issues: {validation_issues}")
        #

        return {
            'is_valid': False,
            'error': f'Database validation error: {str(e)}',
            'confidence': 0.0,
            'flag_id': flag_id
        }
#

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def test_colab_connection():
    """Test if Colab model is accessible"""
    try:
        response = requests.get(f"{COLAB_MODEL_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# Initialize components
verification_logger = VerificationLogger(LOGS_FOLDER)
ocr_extractor = MarksheetOCR(OCR_SPACE_API_KEY)
# db_validator = DatabaseValidator(supabase)


@app.route('/')
def home():
    """API documentation"""
    colab_connected = test_colab_connection()

    return jsonify({
        "service": "Enhanced Jharkhand Document Verification API",
        "version": "2.1",
        "status": "operational",
        "features": [
            "OCR text extraction",
            "Database validation with flagging",
            "ML-based authenticity verification",
            "Batch processing",
            "Comprehensive logging and monitoring"
        ],
        "deployment": "Local API with Colab Model + OCR.space + Supabase",
        "colab_model_url": COLAB_MODEL_URL,
        "colab_connected": colab_connected,
        "cors_enabled": True,
        "workflow": [
            "1. Upload marksheet image",
            "2. Extract text using OCR.space API",
            "3. Parse key information (MS No, Name, College, Total)",
            "4. Validate against Supabase database",
            "5. If valid, check authenticity using ML model",
            "6. Return comprehensive verification result"
        ],
        "endpoints": {
            "enhanced_verification": {
                "url": "/verify/enhanced",
                "method": "POST",
                "description": "Complete marksheet verification with OCR + DB validation + ML authenticity check",
                "parameters": "file (multipart/form-data)"
            },
            "single_verification": {
                "url": "/verify/single",
                "method": "POST",
                "description": "Original ML-only verification",
                "parameters": "file (multipart/form-data)"
            },
            "batch_verification": {
                "url": "/verify/batch",
                "method": "POST",
                "description": "Verify multiple documents via Colab model",
                "parameters": "files (multiple files) or zipfile"
            },
            "ocr_only": {
                "url": "/ocr/extract",
                "method": "POST",
                "description": "Extract text from marksheet using OCR only",
                "parameters": "file (multipart/form-data)"
            },
            "database_lookup": {
                "url": "/database/lookup",
                "method": "POST",
                "description": "Lookup marksheet in database by MS No",
                "parameters": "ms_no (JSON body)"
            },
            "train_model": {
                "url": "/train",
                "method": "POST",
                "description": "Train the ML model via Colab",
                "parameters": "files (original documents)"
            },
            "generate_variations": {
                "url": "/generate/variations",
                "method": "POST",
                "description": "Generate variations via Colab model",
                "parameters": "file (original document), count (optional)"
            },
            "admin_endpoints": {
                "flagged_users": {
                    "url": "/admin/flagged-users",
                    "method": "GET",
                    "description": "Get summary of flagged users and suspicious activities"
                },
                "verification_logs": {
                    "url": "/admin/verification-logs",
                    "method": "GET",
                    "description": "Get verification attempt logs",
                    "parameters": "limit (optional query param)"
                },
                "search_flagged": {
                    "url": "/admin/search-flagged",
                    "method": "POST",
                    "description": "Search flagged users by criteria",
                    "parameters": "ms_no, flag_reason (JSON body)"
                }
            }
        }
    })


# Add preflight OPTIONS handler for CORS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response


@app.route('/verify/enhanced', methods=['POST', 'OPTIONS'])
def verify_enhanced():
    """Enhanced verification with OCR + Database validation + ML authenticity check"""
    try:
        print(f"Received enhanced verification request from: {request.remote_addr}")

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, TIFF'}), 400

        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        verification_result = {
            'status': 'processing',
            'filename': filename,
            'processed_at': datetime.now().isoformat(),
            'steps': {}
        }

        # Step 1: OCR Text Extraction
        print("Step 1: Extracting text using OCR...")
        extracted_text, ocr_error = ocr_extractor.extract_text_from_image(file_path)

        if ocr_error:
            verification_result['status'] = 'failed'
            verification_result['error'] = f'OCR failed: {ocr_error}'
            os.remove(file_path)
            return jsonify(verification_result), 500

        # Step 2: Parse marksheet data
        print("Step 2: Parsing marksheet data...")
        parsed_data = ocr_extractor.parse_marksheet_data(extracted_text)
        verification_result['steps']['ocr_extraction'] = {
            'status': 'success',
            'extracted_data': parsed_data,
            'raw_text_length': len(extracted_text)
        }

        # Step 3: Database validation with comprehensive flagging
        print("Step 3: Validating against database...")
        request_info = {
            'ip': request.remote_addr,
            'filename': filename
        }

        db_validation = db_validator.validate_marksheet(parsed_data, request_info)
        verification_result['steps']['database_validation'] = db_validation

        # Log this verification attempt
        verification_logger.log_verification_attempt({
            'ip_address': request.remote_addr,
            'filename': filename,
            'extracted_data': parsed_data,
            'database_validation': {
                'is_valid': db_validation['is_valid'],
                'confidence': db_validation.get('confidence', 0),
                'flag_id': db_validation.get('flag_id')
            },
            'status': 'database_validation_completed'
        })

        if not db_validation['is_valid']:
            verification_result['status'] = 'invalid'
            verification_result['final_verdict'] = 'INVALID - Database validation failed'
            verification_result['recommendation'] = 'Marksheet details do not match database records'
            os.remove(file_path)
            return jsonify(verification_result)

        # Step 4: ML Authenticity Check (only if database validation passes)
        print("Step 4: Checking authenticity using ML model...")
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, file.content_type)}
                response = requests.post(f"{COLAB_MODEL_URL}/predict", files=files, timeout=30)

            if response.status_code == 200:
                ml_result = response.json()
                verification_result['steps']['ml_authenticity'] = {
                    'status': 'success',
                    'is_authentic': ml_result['is_authentic'],
                    'confidence': ml_result['confidence'],
                    'rf_confidence': ml_result['rf_confidence'],
                    'cnn_confidence': ml_result['cnn_confidence'],
                    'details': ml_result.get('details', {})
                }

                # Final comprehensive verdict
                db_confidence = db_validation['confidence']
                ml_confidence = ml_result['confidence']
                combined_confidence = (db_confidence + ml_confidence) / 2

                is_fully_valid = (
                        db_validation['is_valid'] and
                        ml_result['is_authentic'] and
                        combined_confidence > 0.7
                )

                verification_result['status'] = 'completed'
                verification_result['final_verdict'] = 'AUTHENTIC' if is_fully_valid else 'SUSPICIOUS'
                verification_result['combined_confidence'] = f"{combined_confidence:.1%}"
                verification_result['summary'] = {
                    'database_valid': db_validation['is_valid'],
                    'database_confidence': f"{db_confidence:.1%}",
                    'ml_authentic': ml_result['is_authentic'],
                    'ml_confidence': f"{ml_confidence:.1%}",
                    'overall_status': 'PASS' if is_fully_valid else 'FAIL'
                }

                if is_fully_valid:
                    verification_result[
                        'recommendation'] = 'Marksheet is authentic and verified against database records'
                else:
                    verification_result[
                        'recommendation'] = 'Marksheet requires manual review - some verification checks failed'

            else:
                verification_result['steps']['ml_authenticity'] = {
                    'status': 'failed',
                    'error': f'ML model error: {response.status_code}'
                }
                verification_result['status'] = 'partial_success'
                verification_result['final_verdict'] = 'DATABASE_VALID_ML_FAILED'
                verification_result['recommendation'] = 'Database validation passed but ML authenticity check failed'

        except Exception as e:
            verification_result['steps']['ml_authenticity'] = {
                'status': 'failed',
                'error': str(e)
            }
            verification_result['status'] = 'partial_success'
            verification_result['final_verdict'] = 'DATABASE_VALID_ML_ERROR'

        # Cleanup
        os.remove(file_path)
        print(f"Enhanced verification completed for {filename}")

        return jsonify(verification_result)

    except Exception as e:
        print(f"Enhanced verification error: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'Enhanced verification failed: {str(e)}'}), 500


@app.route('/verify/single', methods=['POST', 'OPTIONS'])
def verify_single_document():
    """Original single document verification (ML only) via Colab model"""
    try:
        print(f"Received verification request from: {request.remote_addr}")

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, TIFF'}), 400

        print(f"Processing file: {file.filename}")

        # Send file to Colab model for prediction
        try:
            files = {'file': (file.filename, file.stream, file.content_type)}

            print(f"Sending request to Colab model: {COLAB_MODEL_URL}")
            response = requests.post(f"{COLAB_MODEL_URL}/predict", files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()

                print(f"Received response from Colab model")

                return jsonify({
                    'status': 'success',
                    'filename': file.filename,
                    'processed_via': 'colab_model',
                    'verification_result': {
                        'document_status': 'AUTHENTIC' if result['is_authentic'] else 'SUSPICIOUS',
                        'confidence_score': f"{result['confidence']:.1%}",
                        'detailed_analysis': {
                            'random_forest_confidence': f"{result['rf_confidence']:.1%}",
                            'cnn_confidence': f"{result['cnn_confidence']:.1%}",
                            'combined_confidence': f"{result['confidence']:.1%}"
                        },
                        'recommendation': (
                            'Document appears authentic and can be trusted.'
                            if result['is_authentic']
                            else 'Document shows signs of tampering. Manual review recommended.'
                        ),
                        'processed_at': datetime.now().isoformat(),
                        'model_details': result.get('details', {})
                    },
                    'security_notice': 'File processed via secure Colab tunnel'
                })
            else:
                print(f"Colab model error: {response.status_code} - {response.text}")
                return jsonify({
                    'error': 'Model prediction failed',
                    'details': f'Colab returned status {response.status_code}',
                    'colab_response': response.text[:200]  # First 200 chars of error
                }), 500

        except requests.exceptions.Timeout:
            return jsonify({'error': 'Colab model timeout. Please try again.'}), 504
        except requests.exceptions.ConnectionError:
            return jsonify({
                'error': 'Cannot connect to Colab model',
                'solution': 'Make sure your Colab notebook is running and ngrok tunnel is active'
            }), 503

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/train', methods=['POST', 'OPTIONS'])
def train_model():
    """Train the ML model via Colab"""
    try:
        print(f"Received training request from: {request.remote_addr}")

        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400

        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400

        print(f"Starting training with {len(files)} files via Colab...")

        # Send files to Colab for training
        try:
            files_data = []
            for file in files:
                if file and allowed_file(file.filename):
                    files_data.append(('files', (file.filename, file.stream, file.content_type)))

            variations_per_image = request.form.get('variations_per_image', 100)
            data = {'variations_per_image': variations_per_image}

            response = requests.post(
                f"{COLAB_MODEL_URL}/train",
                files=files_data,
                data=data,
                timeout=300  # 5 minutes timeout for training
            )

            if response.status_code == 200:
                result = response.json()
                print("Model training completed via Colab!")

                return jsonify({
                    'status': 'success',
                    'message': 'Model trained successfully via Colab!',
                    'processed_via': 'colab_model',
                    'training_results': result.get('training_results', {}),
                    'trained_at': datetime.now().isoformat(),
                    'ready_for_verification': True
                })
            else:
                return jsonify({
                    'error': 'Training failed on Colab',
                    'details': response.text[:200]
                }), 500

        except requests.exceptions.Timeout:
            return jsonify({'error': 'Training timeout. Model training takes time, please wait and check status.'}), 504
        except requests.exceptions.ConnectionError:
            return jsonify({
                'error': 'Cannot connect to Colab for training',
                'solution': 'Ensure Colab notebook is running'
            }), 503

    except Exception as e:
        print(f"Training error: {str(e)}")
        return jsonify({'error': f'Training failed: {str(e)}'}), 500


@app.route('/generate/variations', methods=['POST', 'OPTIONS'])
def generate_document_variations():
    """Generate variations via Colab model"""
    try:
        print(f"Received variation generation request from: {request.remote_addr}")

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        variation_count = int(request.form.get('count', 100))
        if variation_count > 200:
            variation_count = 200

        print(f"Generating {variation_count} variations via Colab...")

        try:
            files = {'file': (file.filename, file.stream, file.content_type)}
            data = {'count': variation_count}

            response = requests.post(
                f"{COLAB_MODEL_URL}/generate/variations",
                files=files,
                data=data,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                print(f"Generated {variation_count} variations successfully via Colab!")

                return jsonify({
                    'status': 'success',
                    'message': f'{variation_count} variations generated successfully via Colab',
                    'processed_via': 'colab_model',
                    'original_filename': file.filename,
                    'variations_generated': result.get('variations_generated', variation_count),
                    'details': {
                        'augmentation_methods_used': [
                            'noise_addition', 'grayscale_conversion', 'dark_spots',
                            'ink_blur', 'brightness_adjustment', 'rotation',
                            'perspective_distortion', 'scan_lines', 'paper_texture'
                        ],
                        'ready_for_training': True,
                        'generated_at': datetime.now().isoformat()
                    }
                })
            else:
                return jsonify({
                    'error': 'Variation generation failed on Colab',
                    'details': response.text[:200]
                }), 500

        except requests.exceptions.Timeout:
            return jsonify({'error': 'Variation generation timeout'}), 504
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to Colab for variation generation'}), 503

    except Exception as e:
        print(f"Variation generation error: {str(e)}")
        return jsonify({'error': f'Variation generation failed: {str(e)}'}), 500


@app.route('/verify/batch', methods=['POST', 'OPTIONS'])
def verify_batch_documents():
    """Verify multiple documents via Colab model"""
    try:
        print(f"Received batch verification request from: {request.remote_addr}")

        job_id = str(uuid.uuid4())
        job_folder = os.path.join(BATCH_FOLDER, job_id)
        os.makedirs(job_folder, exist_ok=True)

        files_to_process = []

        # Handle ZIP file upload
        if 'zipfile' in request.files:
            zip_file = request.files['zipfile']
            if zip_file.filename.endswith('.zip'):
                zip_path = os.path.join(job_folder, 'upload.zip')
                zip_file.save(zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(job_folder)
                for root, dirs, files in os.walk(job_folder):
                    for file in files:
                        if allowed_file(file):
                            files_to_process.append(os.path.join(root, file))

        # Handle multiple file upload
        elif 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(job_folder, filename)
                    file.save(file_path)
                    files_to_process.append(file_path)

        if not files_to_process:
            return jsonify({'error': 'No valid image files found'}), 400

        # Initialize batch job
        batch_jobs[job_id] = {
            'status': 'processing',
            'total_files': len(files_to_process),
            'processed_files': 0,
            'results': [],
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        }

        # Start background processing
        thread = Thread(target=process_batch_job, args=(job_id, files_to_process))
        thread.start()

        print(f"Started batch job {job_id} with {len(files_to_process)} files")

        return jsonify({
            'status': 'success',
            'message': 'Batch processing started via Colab model',
            'job_id': job_id,
            'total_files': len(files_to_process),
            'status_url': f'/batch/status/{job_id}',
            'estimated_time': f'{len(files_to_process) * 5} seconds',
            'processed_via': 'colab_model'
        })
    except Exception as e:
        print(f"Batch processing error: {str(e)}")
        return jsonify({'error': f'Batch processing failed: {str(e)}'}), 500


def process_batch_job(job_id, files_to_process):
    """Background function to process batch jobs via Colab model"""
    try:
        results = []
        print(f"Processing batch job {job_id} via Colab...")

        for i, file_path in enumerate(files_to_process):
            try:
                # Send file to Colab model
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f, 'image/jpeg')}
                    response = requests.post(f"{COLAB_MODEL_URL}/predict", files=files, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    file_result = {
                        'filename': os.path.basename(file_path),
                        'status': 'processed',
                        'is_authentic': result['is_authentic'],
                        'confidence': f"{result['confidence']:.1%}",
                        'verdict': 'AUTHENTIC' if result['is_authentic'] else 'SUSPICIOUS',
                        'rf_confidence': f"{result['rf_confidence']:.1%}",
                        'cnn_confidence': f"{result['cnn_confidence']:.1%}",
                        'details': result.get('details', {})
                    }
                else:
                    file_result = {
                        'filename': os.path.basename(file_path),
                        'status': 'error',
                        'error': f'Colab model error: {response.status_code}'
                    }

                results.append(file_result)
                batch_jobs[job_id]['processed_files'] = i + 1
                batch_jobs[job_id]['results'] = results

                print(f"Processed {i + 1}/{len(files_to_process)} files")
                time.sleep(0.5)  # Prevent overwhelming Colab

            except Exception as e:
                print(f"Error processing file {os.path.basename(file_path)}: {str(e)}")
                results.append({
                    'filename': os.path.basename(file_path),
                    'status': 'error',
                    'error': str(e)
                })

        # Mark job as completed
        batch_jobs[job_id]['status'] = 'completed'
        batch_jobs[job_id]['completed_at'] = datetime.now().isoformat()

        # Generate summary report
        authentic_count = sum(1 for r in results if r.get('is_authentic', False))
        suspicious_count = len(
            [r for r in results if not r.get('is_authentic', True) and r.get('status') == 'processed'])
        batch_jobs[job_id]['summary'] = {
            'total_processed': len(results),
            'authentic_documents': authentic_count,
            'suspicious_documents': suspicious_count,
            'success_rate': f"{(authentic_count / len(results) * 100):.1f}%" if results else "0%"
        }

        print(f"Batch job {job_id} completed successfully via Colab!")

    except Exception as e:
        print(f"Batch job {job_id} failed: {str(e)}")
        batch_jobs[job_id]['status'] = 'failed'
        batch_jobs[job_id]['error'] = str(e)


@app.route('/ocr/extract', methods=['POST', 'OPTIONS'])
def ocr_extract_only():
    """Extract text from marksheet using OCR only"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        # Extract text
        extracted_text, error = ocr_extractor.extract_text_from_image(file_path)

        if error:
            os.remove(file_path)
            return jsonify({'error': error}), 500

        # Parse data
        parsed_data = ocr_extractor.parse_marksheet_data(extracted_text)

        os.remove(file_path)

        return jsonify({
            'status': 'success',
            'filename': filename,
            'extracted_text': extracted_text,
            'parsed_data': parsed_data,
            'processed_at': datetime.now().isoformat()
        })

    except Exception as e:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'OCR extraction failed: {str(e)}'}), 500


@app.route('/database/lookup', methods=['POST', 'OPTIONS'])
def database_lookup():
    """Lookup marksheet in database by MS No"""
    try:
        data = request.get_json()
        if not data or 'ms_no' not in data:
            return jsonify({'error': 'ms_no is required'}), 400

        ms_no = data['ms_no']

        result = supabase.table(SUPABASE_TABLE).select("*").eq('M.S No', ms_no).execute()

        if result.data:
            return jsonify({
                'status': 'found',
                'record': result.data[0],
                'searched_ms_no': ms_no
            })
        else:
            return jsonify({
                'status': 'not_found',
                'searched_ms_no': ms_no,
                'message': 'No record found with this M.S No'
            })

    except Exception as e:
        return jsonify({'error': f'Database lookup failed: {str(e)}'}), 500


@app.route('/admin/flagged-users', methods=['GET'])
def get_flagged_users():
    """Get flagged users summary (admin endpoint)"""
    try:
        summary = verification_logger.get_flagged_users_summary()

        # Add more detailed breakdown
        with open(verification_logger.flagged_users_file, 'r') as f:
            all_flagged = json.load(f)

        # Group by flag reasons
        flag_reasons = {}
        for user in all_flagged:
            reason = user.get('flag_reason', 'unknown')
            if reason not in flag_reasons:
                flag_reasons[reason] = 0
            flag_reasons[reason] += 1

        return jsonify({
            'summary': summary,
            'flag_reasons_breakdown': flag_reasons,
            'total_entries': len(all_flagged),
            'recent_flagged_users': all_flagged[-10:] if all_flagged else []
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get flagged users: {str(e)}'}), 500


@app.route('/admin/verification-logs', methods=['GET'])
def get_verification_logs():
    """Get verification attempt logs (admin endpoint)"""
    try:
        limit = int(request.args.get('limit', 50))

        with open(verification_logger.verification_log_file, 'r') as f:
            logs = json.load(f)

        # Return last N logs
        recent_logs = logs[-limit:] if logs else []

        # Calculate some statistics
        total_attempts = len(logs)
        today_attempts = len([log for log in logs if log['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))])

        return jsonify({
            'recent_logs': recent_logs,
            'statistics': {
                'total_attempts': total_attempts,
                'attempts_today': today_attempts,
                'success_rate': 'Calculated based on logs'  # You can implement this
            }
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get verification logs: {str(e)}'}), 500


@app.route('/admin/search-flagged', methods=['POST'])
def search_flagged_users():
    """Search flagged users by MS No or other criteria"""
    try:
        search_data = request.get_json()
        if not search_data:
            return jsonify({'error': 'Search criteria required'}), 400

        with open(verification_logger.flagged_users_file, 'r') as f:
            flagged_users = json.load(f)

        results = []
        ms_no = search_data.get('ms_no')
        flag_reason = search_data.get('flag_reason')

        for user in flagged_users:
            match = True

            if ms_no and user.get('extracted_data', {}).get('ms_no') != ms_no:
                match = False

            if flag_reason and user.get('flag_reason') != flag_reason:
                match = False

            if match:
                results.append(user)

        return jsonify({
            'search_criteria': search_data,
            'results_count': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@app.route('/batch/status/<job_id>', methods=['GET'])
def get_batch_status(job_id):
    """Get batch processing status"""
    if job_id not in batch_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = batch_jobs[job_id]
    response = {
        'job_id': job_id,
        'status': job['status'],
        'progress': {
            'total_files': job['total_files'],
            'processed_files': job['processed_files'],
            'percentage': f"{(job['processed_files'] / job['total_files'] * 100):.1f}%"
        },
        'started_at': job['started_at']
    }

    if job['status'] == 'completed':
        response['completed_at'] = job['completed_at']
        response['summary'] = job['summary']
        response['download_url'] = f'/download/{job_id}'
        response['results'] = job['results']
    elif job['status'] == 'failed':
        response['error'] = job.get('error', 'Unknown error')

    return jsonify(response)


@app.route('/download/<job_id>', methods=['GET'])
def download_batch_results(job_id):
    """Download batch processing results"""
    if job_id not in batch_jobs or batch_jobs[job_id]['status'] != 'completed':
        return jsonify({'error': 'Results not available'}), 404

    report = {
        'job_id': job_id,
        'processing_summary': batch_jobs[job_id]['summary'],
        'detailed_results': batch_jobs[job_id]['results'],
        'processed_at': batch_jobs[job_id]['completed_at']
    }

    report_path = os.path.join(BATCH_FOLDER, job_id, 'verification_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    return send_from_directory(
        os.path.join(BATCH_FOLDER, job_id),
        'verification_report.json',
        as_attachment=True,
        download_name=f'verification_report_{job_id}.json'
    )


@app.route('/colab/status', methods=['GET'])
def colab_status():
    """Check Colab model connection status"""
    connected = test_colab_connection()

    return jsonify({
        'colab_url': COLAB_MODEL_URL,
        'connected': connected,
        'status': 'online' if connected else 'offline',
        'last_checked': datetime.now().isoformat(),
        'message': 'Colab model is accessible' if connected else 'Cannot reach Colab model. Check if notebook is running.'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check"""
    colab_connected = test_colab_connection()

    # Test database connection
    try:
        test_query = supabase.table(SUPABASE_TABLE).select("count", count="exact").limit(1).execute()
        db_connected = True
    except:
        db_connected = False

    return jsonify({
        'status': 'healthy',
        'service': 'Enhanced Document Verification API',
        'deployment': 'local_api_with_multiple_services',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'colab_model': colab_connected,
            'supabase_database': db_connected,
            'ocr_space': bool(OCR_SPACE_API_KEY and OCR_SPACE_API_KEY != "YOUR_OCR_SPACE_API_KEY_HERE")
        },
        'cors_enabled': True
    })


# Enhanced error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'File too large. Maximum size: 50MB',
        'max_size': '50MB'
    }), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/', '/verify/enhanced', '/verify/single', '/train', '/generate/variations',
            '/verify/batch', '/ocr/extract', '/database/lookup', '/admin/flagged-users',
            '/admin/verification-logs', '/admin/search-flagged', '/health', '/colab/status'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    print(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Starting Enhanced Jharkhand Document Verification API")
    print("=" * 80)

    print(f"📡 Colab Model URL: {COLAB_MODEL_URL}")
    print(
        f"🔍 OCR Service: {'✅ Configured' if OCR_SPACE_API_KEY != 'YOUR_OCR_SPACE_API_KEY_HERE' else '❌ Not configured'}")
    print(f"🗄️  Database: {'✅ Configured' if SUPABASE_URL != 'YOUR_SUPABASE_URL_HERE' else '❌ Not configured'}")

    print("\n🔄 Enhanced Verification Workflow:")
    print("   1. 📤 Upload marksheet image")
    print("   2. 🔍 Extract text using OCR.space API")
    print("   3. 📊 Parse key information (MS No, Name, College, Total)")
    print("   4. 🗄️  Validate against Supabase database")
    print("   5. 🤖 Check authenticity using ML model")
    print("   6. ✅ Return comprehensive verification result")

    print("\n📋 All API Endpoints:")
    print("   🔬 Enhanced Verification: POST /verify/enhanced")
    print("   🤖 ML Verification:      POST /verify/single")
    print("   📦 Batch Verification:   POST /verify/batch")
    print("   🔍 OCR Extract Only:     POST /ocr/extract")
    print("   🗄️  Database Lookup:      POST /database/lookup")
    print("   🏋️  Train Model:          POST /train")
    print("   📄 Generate Variations:  POST /generate/variations")
    print("   🚩 Admin - Flagged Users: GET /admin/flagged-users")
    print("   📊 Admin - Ver. Logs:    GET /admin/verification-logs")
    print("   🔍 Admin - Search Flags: POST /admin/search-flagged")
    print("   📊 Batch Status:         GET /batch/status/<job_id>")
    print("   📥 Download Results:     GET /download/<job_id>")
    print("   🔌 Colab Status:         GET /colab/status")
    print("   ❤️  Health Check:         GET /health")

    print("\n⚠️  Setup Requirements:")
    print("   1. Update OCR_SPACE_API_KEY with your actual API key")
    print("   2. Update SUPABASE_URL and SUPABASE_KEY")
    print("   3. Update COLAB_MODEL_URL with your ngrok URL")
    print("   4. Ensure Colab notebook is running")

    print("\n📁 Log Files Created:")
    print(f"   🚩 Flagged Users: {os.path.join(LOGS_FOLDER, 'flagged_users.json')}")
    print(f"   📊 Verification Logs: {os.path.join(LOGS_FOLDER, 'verification_attempts.json')}")
    print(f"   📝 System Logs: {os.path.join(LOGS_FOLDER, 'verification.log')}")

    print("\n" + "=" * 80)
    print("🚀 Starting Flask server...")
    print("=" * 80)

    # Test connections on startup
    if test_colab_connection():
        print("✅ Colab model connection successful!")
    else:
        print("⚠️  Cannot connect to Colab model")

    try:
        test_query = supabase.table(SUPABASE_TABLE).select("count", count="exact").limit(1).execute()
        print("✅ Supabase database connection successful!")
    except:
        print("⚠️  Cannot connect to Supabase database")

    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
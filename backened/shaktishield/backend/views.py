from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
import os

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Certificate
from .serializers import CertificateSerializer

# Enhanced certificate validation against preloaded certificates
import hashlib
import os
from django.conf import settings
from django.core.cache import cache

def get_reference_certificate_hashes():
    """Get SHA-256 hashes of all reference certificates (cached for performance)"""
    cache_key = 'reference_cert_hashes'
    hashes = cache.get(cache_key)
    
    if hashes is None:
        hashes = set()
        certificates_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
        
        if os.path.exists(certificates_dir):
            for cert_file in os.listdir(certificates_dir):
                cert_path = os.path.join(certificates_dir, cert_file)
                if os.path.isfile(cert_path):
                    try:
                        with open(cert_path, 'rb') as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                            hashes.add(file_hash)
                    except Exception:
                        continue
        
        # Cache for 1 hour (3600 seconds)
        cache.set(cache_key, hashes, 3600)
    
    return hashes

def run_ocr_and_validate(file_path):
    """Validate uploaded certificate against reference certificates using SHA-256 hash comparison"""
    try:
        # Read the uploaded file and compute SHA-256 hash
        with open(file_path, 'rb') as f:
            uploaded_file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Get reference certificate hashes
        reference_hashes = get_reference_certificate_hashes()
        
        # Check if uploaded file hash matches any reference certificate
        if uploaded_file_hash in reference_hashes:
            return "VALID"
        else:
            return "INVALID"
            
    except Exception as e:
        # If any error occurs, mark as invalid
        return "INVALID"

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

@ensure_csrf_cookie
def index_view(request):
    """Serve the government certificate verification portal"""
    from django.template.loader import render_to_string
    from django.template import Template, Context
    
    # Create a professional government portal template
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Government Certificate Verification Portal - Jharkhand Academic Council</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 30%, #2c5364 100%);
            min-height: 100vh;
            color: #333;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 3px solid #c41e3a;
            padding: 20px 0;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            padding: 0 20px;
        }

        .govt-emblem {
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #c41e3a, #ff6b35);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 25px;
            font-size: 32px;
            color: white;
            font-weight: bold;
            border: 3px solid #fff;
            box-shadow: 0 5px 15px rgba(196, 30, 58, 0.3);
        }

        .header-text {
            flex: 1;
        }

        .header-text h1 {
            color: #0f2027;
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .header-text h2 {
            color: #c41e3a;
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .header-text p {
            color: #666;
            font-size: 1em;
            font-weight: 500;
        }

        .container {
            max-width: 800px;
            margin: 40px auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .portal-header {
            background: linear-gradient(135deg, #c41e3a, #ff6b35);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .portal-header h3 {
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .portal-header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .upload-section {
            padding: 40px;
        }

        .upload-area {
            border: 3px dashed #c41e3a;
            border-radius: 15px;
            padding: 60px 40px;
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
            transition: all 0.3s ease;
            cursor: pointer;
            text-align: center;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }

        .upload-area::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(196, 30, 58, 0.1), transparent);
            transition: left 0.5s;
        }

        .upload-area:hover::before {
            left: 100%;
        }

        .upload-area:hover {
            background: linear-gradient(135deg, #fff5f5, #ffffff);
            border-color: #ff6b35;
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(196, 30, 58, 0.2);
        }

        .upload-area.dragover {
            background: linear-gradient(135deg, #fff0f0, #ffffff);
            border-color: #ff6b35;
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 64px;
            color: #c41e3a;
            margin-bottom: 20px;
            display: block;
        }

        .upload-text {
            font-size: 1.4em;
            color: #0f2027;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .upload-subtext {
            color: #666;
            font-size: 1em;
            margin-bottom: 15px;
        }

        .file-requirements {
            color: #888;
            font-size: 0.9em;
            font-style: italic;
        }

        .file-input {
            display: none;
        }

        .verify-btn {
            background: linear-gradient(135deg, #c41e3a, #ff6b35);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }

        .verify-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .verify-btn:hover::before {
            left: 100%;
        }

        .verify-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(196, 30, 58, 0.4);
        }

        .verify-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .result-section {
            margin-top: 30px;
            padding: 30px;
            border-radius: 15px;
            display: none;
            text-align: center;
        }

        .result-valid {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            border: 2px solid #28a745;
            color: #155724;
        }

        .result-invalid {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            border: 2px solid #dc3545;
            color: #721c24;
        }

        .result-icon {
            font-size: 48px;
            margin-bottom: 15px;
            display: block;
        }

        .result-title {
            font-size: 1.6em;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .result-message {
            font-size: 1.1em;
            line-height: 1.6;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 30px;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #c41e3a;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .file-preview {
            max-width: 100%;
            max-height: 200px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                text-align: center;
            }

            .govt-emblem {
                margin: 0 0 20px 0;
            }

            .container {
                margin: 20px;
                border-radius: 15px;
            }

            .upload-section {
                padding: 30px 20px;
            }

            .upload-area {
                padding: 40px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="govt-emblem">JAC</div>
            <div class="header-text">
                <h1>Government of Jharkhand</h1>
                <h2>Jharkhand Academic Council</h2>
                <p>Certificate Verification Portal - Authorized Access Only</p>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="portal-header">
            <h3>🔒 Official Certificate Verification</h3>
            <p>Secure verification system for JAC certificates and marksheets</p>
        </div>

        <div class="upload-section">
            <div class="upload-area" id="uploadArea">
                <span class="upload-icon">📋</span>
                <div class="upload-text">Upload Certificate for Verification</div>
                <div class="upload-subtext">Drop your certificate here or click to browse</div>
                <div class="file-requirements">Supported formats: JPG, PNG, PDF • Maximum size: 10MB</div>
            </div>
            <input type="file" id="certificateFile" class="file-input" accept="image/*,application/pdf" />
            <img id="filePreview" class="file-preview" style="display: none;" />
            
            <button class="verify-btn" id="verifyBtn" style="display: none;" onclick="verifyCertificate()">
                🔍 Verify Certificate
            </button>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Verifying certificate against government database...</p>
            </div>

            <div class="result-section" id="resultSection">
                <span class="result-icon" id="resultIcon"></span>
                <div class="result-title" id="resultTitle"></div>
                <div class="result-message" id="resultMessage"></div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>© 2025 Government of Jharkhand • Jharkhand Academic Council • Secure Certificate Verification System</p>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('certificateFile');
        const verifyBtn = document.getElementById('verifyBtn');
        const filePreview = document.getElementById('filePreview');
        const loading = document.getElementById('loading');
        const resultSection = document.getElementById('resultSection');

        // Upload area click handler
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop handlers
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        // File input change handler
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        function handleFileSelect(file) {
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
            const maxSize = 10 * 1024 * 1024; // 10MB

            if (!validTypes.includes(file.type)) {
                alert('Please select a valid file type (JPG, PNG, PDF)');
                return;
            }

            if (file.size > maxSize) {
                alert('File size must be less than 10MB');
                return;
            }

            // Show file preview for images
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    filePreview.src = e.target.result;
                    filePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                filePreview.style.display = 'none';
            }

            // Update upload area
            uploadArea.innerHTML = `
                <span class="upload-icon">✅</span>
                <div class="upload-text">File Selected: ${file.name}</div>
                <div class="upload-subtext">Ready for verification</div>
            `;

            verifyBtn.style.display = 'block';
            resultSection.style.display = 'none';
        }

        function verifyCertificate() {
            const file = fileInput.files[0];
            if (!file) {
                alert('Please select a certificate file first');
                return;
            }

            // Show loading
            loading.style.display = 'block';
            verifyBtn.style.display = 'none';
            resultSection.style.display = 'none';

            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                loading.style.display = 'none';
                showResult(data);
            })
            .catch(error => {
                loading.style.display = 'none';
                showResult({
                    result: 'INVALID',
                    message: 'Verification failed. Please try again.'
                });
                console.error('Error:', error);
            });
        }

        function showResult(data) {
            const resultIcon = document.getElementById('resultIcon');
            const resultTitle = document.getElementById('resultTitle');
            const resultMessage = document.getElementById('resultMessage');
            
            resultSection.style.display = 'block';

            if (data.result === 'VALID' || data.result === 'Genuine') {
                resultSection.className = 'result-section result-valid';
                resultIcon.textContent = '✅';
                resultTitle.textContent = 'CERTIFICATE VALID';
                resultMessage.textContent = 'This certificate has been successfully verified against the government database and is authentic.';
            } else {
                resultSection.className = 'result-section result-invalid';
                resultIcon.textContent = '❌';
                resultTitle.textContent = 'CERTIFICATE INVALID';
                resultMessage.textContent = 'This certificate could not be verified against the government database. It may be fake or tampered with.';
            }

            verifyBtn.style.display = 'block';
        }

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    </script>
</body>
</html>'''
    
    return HttpResponse(template_content, content_type='text/html')

class CertificateUploadView(APIView):
    def post(self, request, format=None):
        try:
            # Validate file size and type before processing
            file = request.FILES.get('file')
            if not file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Server-side validation
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                return Response({'error': 'File size cannot exceed 10MB'}, status=status.HTTP_400_BAD_REQUEST)
            
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
            if hasattr(file, 'content_type') and file.content_type not in allowed_types:
                return Response({'error': 'Only JPG, PNG, and PDF files are allowed'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = CertificateSerializer(data=request.data)
            if serializer.is_valid():
                certificate = serializer.save()
                # Run certificate validation against preloaded certificates
                result = run_ocr_and_validate(certificate.file.path)
                certificate.result = result
                certificate.save()
                
                # Return JSON response expected by frontend
                response_data = {
                    'id': certificate.id,
                    'result': result,
                    'message': 'Certificate verified successfully' if result == 'VALID' else 'Certificate verification failed',
                    'uploaded_at': certificate.uploaded_at.isoformat()
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid file data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Certificate verification failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

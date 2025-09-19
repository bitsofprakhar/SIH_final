from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
@login_required
def index_view(request):
    """Serve the government certificate verification portal"""
    from django.template.loader import render_to_string
    from django.template import Template, Context
    
    # Create a professional government portal selection template
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

        .portals-section {
            padding: 40px;
        }

        .portals-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }

        .portal-card {
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
            border: 2px solid #e9ecef;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .portal-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(196, 30, 58, 0.1), transparent);
            transition: left 0.5s;
        }

        .portal-card:hover::before {
            left: 100%;
        }

        .portal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(196, 30, 58, 0.2);
            border-color: #c41e3a;
        }

        .portal-icon {
            font-size: 64px;
            margin-bottom: 20px;
            color: #c41e3a;
        }

        .portal-card h4 {
            font-size: 1.5em;
            color: #0f2027;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .portal-card p {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 25px;
            line-height: 1.6;
        }

        .portal-btn {
            background: linear-gradient(135deg, #c41e3a, #ff6b35);
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            font-weight: 600;
            display: inline-block;
            transition: all 0.3s ease;
        }

        .portal-card:hover .portal-btn {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(196, 30, 58, 0.4);
        }

        .logout-section {
            text-align: center;
            border-top: 2px solid #e9ecef;
            padding-top: 30px;
        }

        .logout-btn {
            background: linear-gradient(135deg, #6c757d, #495057);
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-block;
        }

        .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4);
            text-decoration: none;
            color: white;
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

            .portals-section {
                padding: 30px 20px;
            }

            .portals-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .portal-card {
                padding: 30px 20px;
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
            <h3>🏛️ Certificate Verification Portals</h3>
            <p>Select the appropriate portal for your verification needs</p>
        </div>

        <div class="portals-section">
            <div class="portals-grid">
                <div class="portal-card" onclick="location.href='{% url 'single_verification' %}'">
                    <div class="portal-icon">📄</div>
                    <h4>Single Verification</h4>
                    <p>Verify individual certificates one at a time</p>
                    <div class="portal-btn">Enter Portal</div>
                </div>
                
                <div class="portal-card" onclick="location.href='{% url 'batch_verification' %}'">
                    <div class="portal-icon">📑</div>
                    <h4>Batch Verification</h4>
                    <p>Verify multiple certificates simultaneously</p>
                    <div class="portal-btn">Enter Portal</div>
                </div>
                
                <div class="portal-card" onclick="location.href='{% url 'training_verification' %}'">
                    <div class="portal-icon">🎓</div>
                    <h4>Training Verification</h4>
                    <p>Training portal for certificate verification</p>
                    <div class="portal-btn">Enter Portal</div>
                </div>
            </div>
            
            <div class="logout-section">
                <a href="{% url 'logout' %}" class="logout-btn">🚪 Logout</a>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>© 2025 Government of Jharkhand • Jharkhand Academic Council • Secure Certificate Verification System</p>
    </div>

    <script>
        // Simple portal navigation functionality
        function navigateToPortal(url) {
            window.location.href = url;
        }
        
        // Add hover effects for better UX
        document.addEventListener('DOMContentLoaded', function() {
            const portalCards = document.querySelectorAll('.portal-card');
            portalCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
    </script>
</body>
</html>'''
    
    from django.template import Template, RequestContext
    template = Template(template_content)
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

class CertificateUploadView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
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


# Login and Authentication Views
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import user_passes_test

@csrf_protect
def login_view(request):
    """Handle user login with proper CSRF protection"""
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Respect the next parameter for proper redirection
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    # Create login template with proper context handling
    login_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - JAC Certificate Verification Portal</title>
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
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }

        .login-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
            backdrop-filter: blur(10px);
            width: 100%;
            max-width: 400px;
            margin: 20px;
        }

        .login-header {
            background: linear-gradient(135deg, #c41e3a, #ff6b35);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .login-header h2 {
            font-size: 1.8em;
            margin-bottom: 10px;
        }

        .login-header p {
            font-size: 1em;
            opacity: 0.9;
        }

        .login-form {
            padding: 40px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #0f2027;
        }

        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #c41e3a;
        }

        .login-btn {
            width: 100%;
            background: linear-gradient(135deg, #c41e3a, #ff6b35);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(196, 30, 58, 0.4);
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }

        @media (max-width: 480px) {
            .login-container {
                margin: 10px;
            }
            
            .login-form {
                padding: 30px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h2>🏛️ JAC Portal</h2>
            <p>Certificate Verification System</p>
        </div>
        
        <div class="login-form">
            {% if messages %}
                {% for message in messages %}
                    <div class="error-message">{{ message }}</div>
                {% endfor %}
            {% endif %}
            
            <form method="post">
                {% csrf_token %}
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="login-btn">🔐 Login</button>
            </form>
        </div>
    </div>
</body>
</html>'''
    
    from django.template import Template, RequestContext
    template = Template(login_template)
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')


# Portal Views
@login_required
def single_verification_view(request):
    """Single certificate verification portal"""
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Single Verification Portal - JAC</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
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
            justify-content: space-between;
            padding: 0 20px;
        }
        
        .header-left {
            display: flex;
            align-items: center;
        }
        
        .govt-emblem {
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #c41e3a, #ff6b35);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            font-size: 24px;
            color: white;
            font-weight: bold;
        }
        
        .header-text h1 {
            color: #0f2027;
            font-size: 1.8em;
            margin-bottom: 5px;
        }
        
        .nav-links a {
            margin-left: 20px;
            color: #c41e3a;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #ff6b35;
        }
        
        .container {
            max-width: 800px;
            margin: 40px auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        
        .portal-header {
            background: linear-gradient(135deg, #c41e3a, #ff6b35);
            color: white;
            padding: 30px;
            text-align: center;
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
        }
        
        .upload-area:hover {
            background: linear-gradient(135deg, #fff5f5, #ffffff);
            border-color: #ff6b35;
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(196, 30, 58, 0.2);
        }
        
        .upload-icon {
            font-size: 64px;
            color: #c41e3a;
            margin-bottom: 20px;
            display: block;
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
            width: 100%;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-left">
                <div class="govt-emblem">JAC</div>
                <div class="header-text">
                    <h1>Single Certificate Verification</h1>
                </div>
            </div>
            <div class="nav-links">
                <a href="/">← Back to Portals</a>
                <a href="/logout/">Logout</a>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="portal-header">
            <h3>📄 Single Certificate Verification</h3>
            <p>Upload and verify individual certificates</p>
        </div>

        <div class="upload-section">
            <div class="upload-area" onclick="document.getElementById('certificateFile').click()">
                <span class="upload-icon">📋</span>
                <div style="font-size: 1.4em; font-weight: 600; margin-bottom: 10px;">Upload Certificate for Verification</div>
                <div style="color: #666; margin-bottom: 15px;">Click to browse or drag and drop</div>
                <div style="color: #888; font-size: 0.9em;">Supported formats: JPG, PNG, PDF • Max: 10MB</div>
            </div>
            <input type="file" id="certificateFile" style="display: none;" accept="image/*,application/pdf" />
            
            <form id="verificationForm" method="post" action="{% url 'upload' %}" enctype="multipart/form-data" style="display: none;">
                {% csrf_token %}
                <input type="file" name="file" id="hiddenFileInput" accept="image/*,application/pdf" />
            </form>
            
            <button class="verify-btn" onclick="verifyCertificate()">🔍 Verify Certificate</button>
            
            <div class="loading" id="loading" style="display: none; text-align: center; margin-top: 20px;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #c41e3a; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                <p>Verifying certificate...</p>
            </div>
            
            <div id="result" style="display: none; margin-top: 20px; padding: 20px; border-radius: 10px; text-align: center;"></div>
        </div>
    </div>

    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>

    <script>
        function verifyCertificate() {
            const fileInput = document.getElementById('certificateFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a certificate file first');
                return;
            }
            
            // Validate file
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
            if (!validTypes.includes(file.type)) {
                alert('Please select a valid file type (JPG, PNG, PDF)');
                return;
            }
            
            if (file.size > 10 * 1024 * 1024) {
                alert('File size must be less than 10MB');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            
            // Create form data
            const formData = new FormData();
            formData.append('file', file);
            
            // Get CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                showResult(data);
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                showResult({
                    result: 'INVALID',
                    message: 'Verification failed. Please try again.'
                });
            });
        }
        
        function showResult(data) {
            const resultDiv = document.getElementById('result');
            
            if (data.result === 'VALID') {
                resultDiv.style.backgroundColor = '#d4edda';
                resultDiv.style.border = '2px solid #28a745';
                resultDiv.style.color = '#155724';
                resultDiv.innerHTML = '<h3>✅ CERTIFICATE VALID</h3><p>This certificate has been successfully verified.</p>';
            } else {
                resultDiv.style.backgroundColor = '#f8d7da';
                resultDiv.style.border = '2px solid #dc3545';
                resultDiv.style.color = '#721c24';
                resultDiv.innerHTML = '<h3>❌ CERTIFICATE INVALID</h3><p>This certificate could not be verified.</p>';
            }
            
            resultDiv.style.display = 'block';
        }
        
        // Handle file input change
        document.getElementById('certificateFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const uploadArea = document.querySelector('.upload-area');
                uploadArea.innerHTML = `
                    <span class="upload-icon">✅</span>
                    <div style="font-size: 1.4em; font-weight: 600; margin-bottom: 10px;">File Selected: ${file.name}</div>
                    <div style="color: #666; margin-bottom: 15px;">Ready for verification</div>
                `;
            }
        });
    </script>
</body>
</html>'''
    from django.template import Template, RequestContext
    template = Template(template_content)
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


@login_required
def batch_verification_view(request):
    """Batch certificate verification portal"""
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Verification Portal - JAC</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
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
            justify-content: space-between;
            padding: 0 20px;
        }
        
        .header-left {
            display: flex;
            align-items: center;
        }
        
        .govt-emblem {
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #c41e3a, #ff6b35);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            font-size: 24px;
            color: white;
            font-weight: bold;
        }
        
        .header-text h1 {
            color: #0f2027;
            font-size: 1.8em;
            margin-bottom: 5px;
        }
        
        .nav-links a {
            margin-left: 20px;
            color: #c41e3a;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #ff6b35;
        }
        
        .container {
            max-width: 800px;
            margin: 40px auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        
        .portal-header {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .upload-section {
            padding: 40px;
        }
        
        .upload-area {
            border: 3px dashed #28a745;
            border-radius: 15px;
            padding: 60px 40px;
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
            transition: all 0.3s ease;
            cursor: pointer;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .upload-area:hover {
            background: linear-gradient(135deg, #f0fff4, #ffffff);
            border-color: #20c997;
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(40, 167, 69, 0.2);
        }
        
        .upload-icon {
            font-size: 64px;
            color: #28a745;
            margin-bottom: 20px;
            display: block;
        }
        
        .verify-btn {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-left">
                <div class="govt-emblem">JAC</div>
                <div class="header-text">
                    <h1>Batch Certificate Verification</h1>
                </div>
            </div>
            <div class="nav-links">
                <a href="/">← Back to Portals</a>
                <a href="/logout/">Logout</a>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="portal-header">
            <h3>📑 Batch Certificate Verification</h3>
            <p>Upload and verify multiple certificates at once</p>
        </div>

        <div class="upload-section">
            <div class="upload-area" onclick="document.getElementById('batchFiles').click()">
                <span class="upload-icon">📁</span>
                <div style="font-size: 1.4em; font-weight: 600; margin-bottom: 10px;">Upload Multiple Certificates</div>
                <div style="color: #666; margin-bottom: 15px;">Select multiple files for batch processing</div>
                <div style="color: #888; font-size: 0.9em;">Supported formats: JPG, PNG, PDF • Max: 10MB each</div>
            </div>
            <input type="file" id="batchFiles" style="display: none;" multiple accept="image/*,application/pdf" />
            
            <button class="verify-btn" onclick="verifyBatch()">🔍 Verify All Certificates</button>
        </div>
    </div>

    <script>
        function verifyBatch() {
            alert('Batch certificate verification functionality will be implemented here.');
        }
    </script>
</body>
</html>'''
    from django.template import Template, RequestContext
    template = Template(template_content)
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))


@login_required
def training_verification_view(request):
    """Training certificate verification portal"""
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Training Verification Portal - JAC</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
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
            justify-content: space-between;
            padding: 0 20px;
        }
        
        .header-left {
            display: flex;
            align-items: center;
        }
        
        .govt-emblem {
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #c41e3a, #ff6b35);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            font-size: 24px;
            color: white;
            font-weight: bold;
        }
        
        .header-text h1 {
            color: #0f2027;
            font-size: 1.8em;
            margin-bottom: 5px;
        }
        
        .nav-links a {
            margin-left: 20px;
            color: #c41e3a;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #ff6b35;
        }
        
        .container {
            max-width: 800px;
            margin: 40px auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        
        .portal-header {
            background: linear-gradient(135deg, #6f42c1, #e83e8c);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .training-section {
            padding: 40px;
        }
        
        .training-card {
            border: 2px solid #6f42c1;
            border-radius: 15px;
            padding: 40px;
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
            text-align: center;
            margin-bottom: 30px;
        }
        
        .training-icon {
            font-size: 64px;
            color: #6f42c1;
            margin-bottom: 20px;
            display: block;
        }
        
        .training-btn {
            background: linear-gradient(135deg, #6f42c1, #e83e8c);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-left">
                <div class="govt-emblem">JAC</div>
                <div class="header-text">
                    <h1>Training Certificate Verification</h1>
                </div>
            </div>
            <div class="nav-links">
                <a href="/">← Back to Portals</a>
                <a href="/logout/">Logout</a>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="portal-header">
            <h3>🎓 Training Certificate Verification</h3>
            <p>Training portal for learning certificate verification process</p>
        </div>

        <div class="training-section">
            <div class="training-card">
                <span class="training-icon">🎯</span>
                <div style="font-size: 1.4em; font-weight: 600; margin-bottom: 15px;">Training Module</div>
                <div style="color: #666; margin-bottom: 20px;">Learn how to effectively verify certificates using our training samples</div>
                
                <button class="training-btn" onclick="startTraining()">🚀 Start Training Session</button>
            </div>
        </div>
    </div>

    <script>
        function startTraining() {
            alert('Training certificate verification functionality will be implemented here.');
        }
    </script>
</body>
</html>'''
    from django.template import Template, RequestContext
    template = Template(template_content)
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))

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
    return render(request, 'index.html')

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
    
    return render(request, 'login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

@login_required
def single_verification_view(request):
    """Single certificate verification portal"""
    return render(request, 'single_verification.html')

@login_required
def batch_verification_view(request):
    """Batch certificate verification portal"""
    return render(request, 'batch_verification.html')

@login_required  
def training_verification_view(request):
    """Training certificate verification portal"""
    return render(request, 'training_verification.html')
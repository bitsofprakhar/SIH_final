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

# Dummy OCR/validation (replace with real call)
def run_ocr_and_validate(file_path):
    # Integrate your OCR and AI here
    # For demo, just return a dummy result
    return "Genuine" if "valid" in file_path else "Fake"

def index_view(request):
    """Serve the main application page"""
    # Read the HTML file and serve it with the correct API URL
    html_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'superuser.html')
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Update the API URL to use the current domain
        # Replace the commented HTML and uncomment it
        content = content.replace('<!--<!DOCTYPE html>', '<!DOCTYPE html>')
        content = content.replace('<!--</html>-->', '</html>')
        content = content.replace('<!--', '')
        content = content.replace('-->', '')
        
        # Update the API base URL to use the current domain
        current_domain = request.get_host()
        content = content.replace("const API_BASE_URL = 'http://127.0.0.1:5000';", 
                                f"const API_BASE_URL = 'https://{current_domain}';")
        
        # Fix the static file references
        content = content.replace('href="style.css"', 'href="/static/style.css"')
        content = content.replace('src="scripts.js"', 'src="/static/scripts.js"')
        
        return HttpResponse(content.encode('utf-8'), content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(b"Frontend not found", status=404)

class CertificateUploadView(APIView):
    def post(self, request, format=None):
        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            certificate = serializer.save()
            # Run OCR and validation after save
            result = run_ocr_and_validate(certificate.file.path)
            certificate.result = result
            certificate.save()
            return Response(CertificateSerializer(certificate).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

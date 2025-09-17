from django.shortcuts import render

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

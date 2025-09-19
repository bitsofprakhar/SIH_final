from django.db import models

# Create your models here.
class Certificate(models.Model):
    file = models.FileField(upload_to='uploads/')  # Upload to separate directory
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(blank=True, null=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.file:
            # Validate file size (10MB max)
            if self.file.size > 10 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 10MB')
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
            if hasattr(self.file, 'content_type') and self.file.content_type not in allowed_types:
                raise ValidationError('Only JPG, PNG, and PDF files are allowed')
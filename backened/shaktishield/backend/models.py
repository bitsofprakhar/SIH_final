from django.db import models

# Create your models here.
class Certificate(models.Model):
    file = models.FileField(upload_to='certificates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(blank=True, null=True)
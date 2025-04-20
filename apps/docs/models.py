from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Document(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    original_name = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=120, blank=True, null=True)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    txt_file = models.FileField(upload_to='texts/', null=True, blank=True)
    upload_date = models.DateTimeField(default=timezone.now)
    is_processed = models.BooleanField(default=False)
    extracted = models.BooleanField(default=False)

    def __str__(self):
        return self.original_name

    def delete(self, *args, **kwargs):
        # Delete both the original file and text file from storage when the model instance is deleted
        if self.file:
            self.file.delete()
        if self.txt_file:
            self.txt_file.delete()
        super().delete(*args, **kwargs)

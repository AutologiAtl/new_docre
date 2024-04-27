from django.db import models

class UploadedFile(models.Model):
    file1 = models.FileField(upload_to='uploads/', null=True, blank=True)
    file2 = models.FileField(upload_to='uploads/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file1.name} / {self.file2.name}"
    
class UserProfile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.username

class PathInformation(models.Model):
    icm = models.CharField(max_length=50, null=True, blank=True)
    icm1 = models.CharField(max_length=50, null=True, blank=True)
    excel_download = models.CharField(max_length=100, null=True, blank=True)
    file = models.CharField(max_length=100000, null=True, blank=True)
    df1_json = models.CharField(max_length=100000, null=True, blank=True)
    excel_path = models.CharField(max_length=500, null=True, blank=True)
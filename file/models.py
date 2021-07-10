import os
from django.db import models
from django.contrib.auth.models import User

class UploadFile(models.Model):
    file = models.FileField(upload_to="uploads")
    file_owner = models.ForeignKey(User, related_name='file_owner', on_delete=models.CASCADE)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    identifier = models.CharField(max_length=100)
    mime_type = models.CharField(max_length=100)
    size_mb = models.CharField(max_length=100)
    size_bytes = models.CharField(max_length=100)
    downloaded = models.IntegerField(default=0)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    authorised_user = models.CharField(max_length=30, blank=True, null=True)
    restricted_by_user = models.BooleanField(default=False)
    restricted_by_country = models.BooleanField(default=False)
    location = models.CharField(max_length=100)
    thumbnail = models.ImageField()

    def __str__(self):
        return self.file_owner.username

    def just_downloaded(self):
        self.downloaded += 1
        self.save()

    def total_reviews(self):
        return self.file_review.count()

    def save(self,*args,**kwargs):
        if 'image' in self.mime_type:
            self.thumbnail = self.file
        else:
            for image in os.listdir(os.getcwd()+'\media\images'):
                if image.split(".")[0] in self.mime_type:
                    self.thumbnail = f'images/{image}'
        super().save(*args, **kwargs)


class Review(models.Model):
    file_review = models.ForeignKey(UploadFile, related_name='file_review', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='reviewer', on_delete=models.CASCADE)
    rating = models.DecimalField(decimal_places=2, max_digits=10)
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.file_review.name}reviewed by {self.reviewer}'


# class Shares(models.Model):

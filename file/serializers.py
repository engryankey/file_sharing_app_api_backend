from rest_framework import serializers
from django.urls import reverse
from .models import *

class ListUploadFileSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UploadFile
        fields = [
           'file', 'owner', 'uploaded_date', 'location',
            'identifier', 'mime_type', 'size_mb', 'restricted_by_country',
            'size_bytes', 'downloaded', 'title', 'restricted_by_user',
            'description', 'authorised_user', 'thumbnail', 'link',
            ]

    def get_link(self, obj):
        result = {
            'rel': 'files',
            'url': reverse('files:file_detail', kwargs={'identifier': obj.identifier})
        }
        return result

    def get_owner(self, obj):
        return {
            'username': obj.file_owner.username,
            'first_name': obj.file_owner.first_name
        }


class DeatailUploadFileSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UploadFile
        fields = [
            'file', 'owner', 'uploaded_date', 'location',
            'identifier', 'mime_type', 'size_mb', 'restricted_by_country',
            'size_bytes', 'downloaded', 'title', 'restricted_by_user',
            'description', 'authorised_user', 'thumbnail', 'link',
            ]

    def get_link(self, obj):
        result = {
            'rel': 'files',
            'url': reverse('files:file_detail', kwargs={'identifier': obj.identifier})
        }
        return result

    def get_owner(self, obj):
        return {
            'username': obj.file_owner.username,
            'first_name': obj.file_owner.first_name
        }


class DownloadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFile
        fields = ['file']

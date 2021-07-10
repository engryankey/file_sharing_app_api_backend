import os
from django.contrib.auth.models import User
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.http.response import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
import firebase_admin
from firebase_admin import credentials
from .models import UploadFile
from .serializers import (
    ListUploadFileSerializer,
    DeatailUploadFileSerializer,
    DownloadFileSerializer,
)
import secrets
import mimetypes
import json


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def files(request):
    owner = request.user

    if request.method == "POST":
        file = request.FILES.get("file")
        data = request.data
        UploadFile.objects.create(
            file_owner=owner,
            file=file,
            identifier=secrets.token_hex(4),
            title=data["title"],
            description=data["description"],
            authorised_user= data["authorised_user"] if data["restricted_by_user"] == "true" else None,
            size_bytes=data["bytes"],
            size_mb=data["mb"],
            mime_type=mimetypes.guess_type(data["file_name"], strict=True)[0],
            location=data["location"],
            restricted_by_user= True if data["restricted_by_user"] == "true" else False,
            restricted_by_country= True if data["restricted_by_country"] == "true" else False,
        )
        return Response(
            {"message": "File uploaded successfully."}, status=status.HTTP_201_CREATED
        )

    elif request.method == "GET":

        files = UploadFile.objects.filter(file_owner=owner)

        serializer = ListUploadFileSerializer(files, many=True)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK,
        )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def file_detail_view(request, identifier):
    try:
        file = UploadFile.objects.get(identifier=identifier.split('-')[0])

        if request.user == file.file_owner:
            if request.method == "GET":
                serializer = DeatailUploadFileSerializer(file, many=False)
                return Response(
                    {"data": serializer.data,},
                    status=status.HTTP_200_OK,
                )

            elif request.method == "DELETE":
                file.delete()
                return Response(
                    {
                        "message": "File successfully deleted",
                    },
                    status=status.HTTP_200_OK,
                )

            elif request.method == "PUT":
                data = request.data
                print(request.headers)
                try:
                    file = UploadFile.objects.get(identifier=identifier.split('-')[0])
                    if data['category'] == 'by_user':
                        UploadFile.objects.filter(identifier=identifier.split('-')[0]).update(restricted_by_user = not file.restricted_by_user)
                        return Response(
                            {
                                "message": "Update successful",
                            },
                            status=status.HTTP_200_OK,
                        )
                    
                    elif data['category'] == 'by_country':
                        UploadFile.objects.filter(identifier=identifier.split('-')[0]).update(restricted_by_country = not file.restricted_by_country)
                        return Response(
                            {
                                "message": "Update successful",
                            },
                            status=status.HTTP_200_OK,
                        )
                    
                    else:
                        return Response(
                            {
                                "message": "Error",
                            },
                            status=status.HTTP_409_CONFLICT,
                        )
                except ObjectDoesNotExist:
                    return Response(
                        {"message": "This file does not exist on here"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

        else:
            if request.method == "GET":
                print(identifier)
                if file.restricted_by_user:
                    if file.authorised_user != request.user:
                        return Response(
                            {
                                "message": "Unauthorized user",
                            },
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                    else:
                        serializer = DeatailUploadFileSerializer(file, many=False)
                        return Response(
                            {"data": serializer.data, "methods": "GET"},
                            status=status.HTTP_200_OK,
                        )
                elif file.restricted_by_country:
                    if file.location.lower() != identifier.split('-')[1].lower():
                        return Response(
                            {
                                "message": "Unauthorized location",
                            },
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                    else:
                        serializer = DeatailUploadFileSerializer(file, many=False)
                        return Response(
                            {"data": serializer.data, "methods": "GET"},
                            status=status.HTTP_200_OK,
                        )
                else:
                    serializer = DeatailUploadFileSerializer(file, many=False)
                    return Response(
                        {"data": serializer.data, "message": "Successful"},
                        status=status.HTTP_200_OK,
                    )

    except ObjectDoesNotExist:
        return Response(
            {"message": "This file does not exist on here"},
            status=status.HTTP_404_NOT_FOUND,
        )



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_file_view(request, identifier):
    if request.method == 'GET':

        try:
            file = UploadFile.objects.get(identifier=identifier.split('-')[0])

            if (file.restricted_by_user and request.user != file.authorised_user) or (file.restricted_by_country and file.location != identifier.split('-')[1].lower()):
                return HttpResponse(
                    "You do not have access to this file",
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            else:
                file.just_downloaded()
                file_path = open(file.file.path, "rb")
                print(file_path)
                print(file.file.path)
                response = HttpResponse(file_path, content_type=file.mime_type, status=status.HTTP_200_OK)
                response['Content-Disposition'] = f"attachment; filename={file.file.path.split('uploads')[1][1:]}"
                return response

        except ObjectDoesNotExist:
            return Response(
                {"message": "This file does not exist on here"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def validate_file(request, identifier):
    print(identifier)
    try:
        file = UploadFile.objects.get(identifier = identifier.lower())
        return Response(
            {"message": "Successful"},
            status=status.HTTP_200_OK,
        )

    except UploadFile.DoesNotExist:
        return Response(
            {"message": "Failed"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def share_file(request, username, identifier):
    receiver = User.objects.get(username = username)
    key_path = os.getcwd()+'\servicekey.json'
    cred = credentials.Certificate(key_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass
    token = cred.get_access_token().access_token
    url = 'https://fcm.googleapis.com/v1/projects/temishare/messages:send'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "message":{
            "token": str(receiver.token.token),
            "notification":{
                "body":f"{str(request.user.username.upper())} shared a file with you.",
                "title":f"File from {str(request.user.username.upper())}"
            },
            "data":{
                "identifier": identifier,
                "click_action": "FLUTTER_CLICK_ACTION"

            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return Response(
            {"message": "Successful"},
            status=status.HTTP_200_OK,
        )
    else:
        print(f'RESPONSE {response.json()}')
        return Response(
            {"message": "Failed"},
            status=status.HTTP_404_NOT_FOUND,
        )
    

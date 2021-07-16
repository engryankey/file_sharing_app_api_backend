from django.contrib.auth.models import User
from .models import FireToken
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializerToken
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
def register_user(request):
    data = request.data

    if User.objects.filter(username = data['username']):
        return Response(
            {'message': 'Username exists'},
            status=status.HTTP_409_CONFLICT
        )

    elif User.objects.filter(username = data['email']):
        return Response(
            {'message': 'Email exists'},
            status=status.HTTP_409_CONFLICT
        )

    else:
        user = User.objects.create_user(
            first_name = data['first_name'],
            last_name = data['last_name'],
            username = data['username'].lower(),
            email = data['email'],
            password = data['password']
        )

        serializer = UserSerializerToken(user, many=False)
        return Response(
            {
                'data': serializer.data,
                'message': 'Regristration successful.'
            }, 
            status=status.HTTP_201_CREATED
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def validate_username(request, username):
    try:
        user = User.objects.get(username = username)
        return Response(
            {"message": "Successful", "first_name": user.first_name},
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"message": "Failed"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def receive_token(request, token):
    try:
        FireToken.objects.get(user = request.user)
        FireToken.objects.filter(user = request.user).update(token = token)
        return Response(
            {"token": token},
            status=status.HTTP_200_OK,
        )
    except FireToken.DoesNotExist:
        FireToken.objects.create(
            user = request.user,
            token = token
            )
        return Response(
            {"token": token},
            status=status.HTTP_200_OK,
        )
    
    

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


@api_view(["POST"])
def register(request):
    data = request.data

    if User.objects.filter(username=data.get("username")).exists():
        return Response({"detail": "Username already taken"}, status=400)

    if User.objects.filter(email=data.get("email")).exists():
        return Response({"detail": "Email already registered"}, status=400)

    user = User.objects.create(
        username=data["username"],
        email=data["email"],
        password=make_password(data["password"]),
    )

    return Response({"detail": "User created successfully"}, status=201)

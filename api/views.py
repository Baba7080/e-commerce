from django.shortcuts import render
from app.models import *
from rest_framework import generics, status
from .serializer import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "status": 201,
                "message": "You have successfully registered",
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            
            "status":200,
            "message": "User Logged in Successfully",
            "token": token.key,
        })


class ProductDetailsView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": 200,
                "message": "Product list retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": 201,
                    "message": "Product created successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "message": "Failed to create product",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_id):
        products = Product.objects.filter(category_id=category_id)
        
        serializer = ProductSerializer(products, many=True)
        
        return Response({
            "status": 200,
            "message": "Successfully fetched products",
            "data": serializer.data
        }, status=status.HTTP_200_OK)




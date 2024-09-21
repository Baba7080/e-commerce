from django.shortcuts import render
from app.models import *
from rest_framework import generics, status
from .serializer import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import uuid

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

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(
            {
                "status": 200,
                "message": "Product retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": 200,
                    "message": "Product updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "message": "Failed to update product",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response(
            {
                "status": 204,
                "message": "Product deleted successfully"
            },
            status=status.HTTP_204_NO_CONTENT
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
    

class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            
            return Response({
                "status": 200,
                "message": "Successfully fetched product",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({
                "status": 404,
                "message": "Product not found"
            }, status=status.HTTP_404_NOT_FOUND)
        

class CartManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart_data = request.data.get('cart_items', [])

        if not cart_data:
            return Response({'message': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        cart_entry, created = CartManagementModels.objects.get_or_create(user=user, defaults={'add_to_cart': []})

        cart_items = cart_entry.add_to_cart

        for item in cart_data:
            product_id = item.get('product')
            quantity = item.get('quantity', 1)

            product = Product.objects.filter(id=product_id).first()
            if not product:
                return Response({'message': f'Product with ID {product_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            for entry in cart_items:
                if entry['product'] == product_id:
                    entry['quantity'] += quantity
                    break
            else:
                cart_items.append({'product': product_id, 'quantity': quantity}) 

        cart_entry.add_to_cart = cart_items
        cart_entry.save()

        return Response({
            "status": 200,
            "message": "Items added to cart successfully",
        }, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        user = request.user

        cart_entry = CartManagementModels.objects.filter(user=user).first()

        if not cart_entry or not cart_entry.add_to_cart:
            return Response({'message': 'Your cart is empty'}, status=status.HTTP_200_OK)

        cart_items = []
        for item in cart_entry.add_to_cart:
            product = Product.objects.filter(id=item['product']).first()
            if product:
                cart_items.append({
                    'product_id': product.id,
                    'title': product.title,
                    'quantity': item['quantity'],
                    'selling_price': product.selling_price,
                    'discounted_price': product.discounted_price,
                    'product_image': request.build_absolute_uri(product.product_image.url) if product.product_image else None
                })

        return Response({"status": 200,
            "message": "Cart fetched successfully",
            "data": cart_items
        }, status=status.HTTP_200_OK)
    
class IncreaseQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        user = request.user

        cart_entry = CartManagementModels.objects.filter(user=user).first()
        if not cart_entry or not cart_entry.add_to_cart:
            return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart_entry.add_to_cart
        for item in cart_items:
            if item['product'] == product_id:
                item['quantity'] += 1 
                cart_entry.add_to_cart = cart_items
                cart_entry.save()
                return Response({
                    "status": 200,
                    "message": "Product quantity increased",
                  
                }, status=status.HTTP_200_OK)

        return Response({'message': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)
   

class DecreaseQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        user = request.user

        cart_entry = CartManagementModels.objects.filter(user=user).first()
        if not cart_entry or not cart_entry.add_to_cart:
            return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart_entry.add_to_cart
        for item in cart_items:
            if item['product'] == product_id:
                if item['quantity'] > 1:
                    item['quantity'] -= 1  
                    cart_entry.add_to_cart = cart_items
                    cart_entry.save()
                    return Response({
                        "status": 200,
                        "message": "Product quantity decreased",
                       
                    }, status=status.HTTP_200_OK)
                else:
                    cart_items.remove(item)
                    cart_entry.add_to_cart = cart_items
                    cart_entry.save()
                    return Response({
                        "status": 200,
                        "message": "Product removed from cart",
                        
                    }, status=status.HTTP_200_OK)

        return Response({'message': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)
    
class RemoveCartProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        user = request.user

        cart_entry = CartManagementModels.objects.filter(user=user).first()
        if not cart_entry or not cart_entry.add_to_cart:
            return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart_entry.add_to_cart
        for item in cart_items:
            if item['product'] == product_id:
                cart_items.remove(item)
                cart_entry.add_to_cart = cart_items
                cart_entry.save()
                return Response({
                    "status": 200,
                    "message": "Product removed from cart",
                    
                }, status=status.HTTP_200_OK)

        return Response({'message': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)
    

    

    




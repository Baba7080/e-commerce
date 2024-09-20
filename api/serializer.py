from rest_framework import serializers
from app.models import *
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ['id', 'category']  

class ProductSerializer(serializers.ModelSerializer):
    
    category_name = serializers.CharField(source='category.category', read_only=True)  

    class Meta:
        model = Product
        fields = ['id', 'title', 'selling_price', 'discounted_price', 'description', 'brand', 'category', 'category_name', 'product_image']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)  
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
           
            user = authenticate(username=username, password=password)
            
            if user:
                data['user'] = user
            else:
                raise serializers.ValidationError("Username and Password not matched")
        else:
            raise serializers.ValidationError("Must include 'Username' and 'password'.")
        
        return data







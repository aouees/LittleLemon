from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User,Group
from rest_framework.validators import UniqueTogetherValidator


class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','email','username','first_name','last_name']
        
class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(),
            default=serializers.CurrentUserDefault(),
    )
    quantity=serializers.IntegerField(min_value=1)
    menuitem=MenuItemSerializer(read_only=True)
    unit_price=serializers.DecimalField(max_digits=6,decimal_places=2,read_only=True)
    price=serializers.DecimalField(max_digits=6,decimal_places=2,read_only=True)
    menuitem_id=serializers.IntegerField(write_only=True)
    class Meta:
        model=Cart
        fields=['user','menuitem','menuitem_id','quantity','unit_price','price']  
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=['user', 'menuitem_id']
            )
        ]
    def create(self,validated_data):
        menuitem_id=validated_data['menuitem_id']
        menuitem=MenuItem.objects.get(pk=menuitem_id)
        validated_data['unit_price']=menuitem.price
        validated_data['price']=menuitem.price*validated_data["quantity"]
        return super().create(validated_data)
       
class OrderItemSerializer(serializers.ModelSerializer):
    menuitem=MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['quantity','unit_price','price','menuitem']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True,read_only=True)
    delivery_crew=UserSerializer(read_only=True)
    user=UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id','status','total','date','user','delivery_crew','order_items']
  
        
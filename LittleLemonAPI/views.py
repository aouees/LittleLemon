from rest_framework import generics
from .models import *
from django.contrib.auth.models import User,Group
from .serializers import *
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.contrib.auth.decorators import user_passes_test
from .permissions import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404,get_list_or_404
from datetime import date

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticated()]
        elif self.request.method=='POST':
            return [IsAuthenticated(),IsAdminUser()]
        return [IsAuthenticated(),IsManager()]

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'featured']
    filterset_fields = ['price', 'featured']
    search_fields = ['title']
    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticated()]
        elif self.request.method=='POST':
            return [IsAuthenticated(),IsAdminUser()]
        return [IsAuthenticated(),IsManager()]  
        
    
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticated()]
        elif self.request.method=='DELETE':
            return [IsAuthenticated(),IsAdminUser()]
        return [IsAuthenticated(),IsManager()]  

class ManagersView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]
    
    def get(self,request):
        users= Group.objects.get(name='manager').user_set.all()
        data=UserSerializer(users,many=True).data
        return Response(data,status.HTTP_201_CREATED)
    
    def post(self,request):
        if 'username' in request.data:
            username=request.data['username']
            user=get_object_or_404(User,username=username)
            managers=Group.objects.get(name='manager')
            managers.user_set.add(user)
            msg='user '+username+' added succesfully as manager'
            return Response({'detail':msg},status.HTTP_201_CREATED)
        else :
            return Response({'detail':'we not found username in payloud'},status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,userId):
        user=get_object_or_404(User,pk=userId)
        if not user.groups.filter(name='manager').exists():
            return Response({'detail':'this user not found'},status.HTTP_404_NOT_FOUND)
        managers=Group.objects.get(name='manager')
        managers.user_set.remove(user)
        msg='user '+str(user.username) +' deleted succesfully as manager'
        return Response({'detail':msg},status.HTTP_200_OK)

class DeliveryView(APIView):
    permission_classes = [IsAuthenticated,IsManager]
    
    def get(self,request):
        users= Group.objects.get(name='delivery').user_set.all()
        data=UserSerializer(users,many=True).data
        return Response(data,status.HTTP_201_CREATED)
    
    def post(self,request):
        if 'username' in request.data:
            username=request.data['username']
            user=get_object_or_404(User,username=username)
            delivery=Group.objects.get(name='delivery')
            delivery.user_set.add(user)
            msg='user '+username+' added succesfully as delivery'
            return Response({'detail':msg},status.HTTP_201_CREATED)
        else :
            return Response({'detail':'we not found username in payloud'},status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,userId):
        user=get_object_or_404(User,pk=userId)
        delivery=Group.objects.get(name='delivery')
        delivery.user_set.remove(user)
        msg='user '+str(user.username) +' deleted succesfully as delivery'
        return Response({'detail':msg},status.HTTP_200_OK)

class CartView(generics.ListCreateAPIView,generics.DestroyAPIView):
    queryset=Cart.objects.all()
    serializer_class=CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersView(APIView):
    permission_classes=[IsAuthenticated] 
    def get(self, request):
        orders =  Order.objects.all().prefetch_related('order_items')
        if request.user.groups.filter(name='manager').exists():
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        elif request.user.groups.filter(name='delivery').exists():
            orders = orders.filter(delivery_crew=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        else :
            orders = orders.filter(user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
    def post(self,request):
        carts = get_list_or_404(Cart,user=request.user) 
        order=Order(user=request.user,date=date.today(),total=0)
        order.save()
        sum=0
        for cart in carts:
            sum=sum+cart.price
            OrderItem(menuitem=cart.menuitem,price=cart.price,quantity=cart.quantity,unit_price=cart.unit_price,order=order).save()
            cart.delete()
        order.total=sum
        order.save()
        return Response(OrderSerializer(order).data)
    
class SingelOrderView(APIView):   
    permission_classes=[IsAuthenticated]
        
    def get(self, request,orderId):
        order =  get_object_or_404(Order,pk=orderId)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    def patch(self,request,orderId):
        order = get_object_or_404(Order,pk=orderId)
        if request.user.groups.filter(name='manager').exists():
            if 'status' in request.data:
                status=request.data['status']
                order.status=status
            if 'delivery_id' in request.data:
                delivery_id=request.data['delivery_id']
                delivery=get_object_or_404(User,pk=delivery_id)
                if delivery.groups.filter(name='delivery').exists() :
                    order.delivery_crew=delivery
                else :
                    return Response({'detail':'no dilevery founded'},404)
            order.save()
            return Response(OrderSerializer(order).data)
        elif request.user.groups.filter(name='delivery').exists():
            if 'status' in request.data:
                status=request.data['status']
                order.status=status
            order.save()
            return Response(OrderSerializer(order).data)
        else:
            return Response({"detail": "You do not have permission to perform this action."},status= 403)
        
    def delete(self,request,orderId):
        order = get_object_or_404( Order,pk=orderId)
        order.delete()
        return Response({'detail':'deleted order done'},status.HTTP_204_NO_CONTENT)        
    
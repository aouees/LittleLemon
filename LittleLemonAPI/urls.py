from django.urls import path 
from . import views 
  
urlpatterns = [ 
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('category/',views.CategoriesView.as_view()),
    path('groups/manager/users/',views.ManagersView.as_view()),
    path('groups/manager/users/<int:userId>',views.ManagersView.as_view()),
    path('groups/delivery-crew/users/',views.DeliveryView.as_view()),
    path('groups/delivery-crew/users/<int:userId>',views.DeliveryView.as_view()),
    path('cart/menu-items/',views.CartView.as_view()),
    path('orders/',views.OrdersView.as_view()),
    path('orders/<int:orderId>',views.SingelOrderView.as_view()),
] 
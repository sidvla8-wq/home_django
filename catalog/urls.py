from django.urls import path

from . import views

# urlpatterns = [
#     path('', views.HomeView.as_view(), name='home'),
#     path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
#     path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
#     path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
#     path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
#     path('contacts/', views.ContactView.as_view(), name='contacts'),
# ]
urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("create/", views.product_create, name="product_create"),
    path("<int:pk>/update/", views.product_update, name="product_update"),
    path("<int:pk>/delete/", views.product_delete, name="product_delete"),
]
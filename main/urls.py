from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.mainpage, name='home'),
    path('register', views.RegisterUser.as_view(), name='register'),
    path('login', views.LoginUser.as_view(), name='login'),
    path('logout', views.logout_user, name='logout'),
    path('profile', views.profile, name='profile'),
    path('product/<int:id>', views.ProductPage),
    path('product/<int:id>/', views.ProductPage, name="product"),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('cart', views.CartPage, name="cart"),
    path('special', views.special, name="special"),
    path('category/<int:id>/', views.categorys, name="category"),
    path('add-product/', views.add_product, name='add_product'),
    path('load-categories/', views.load_categories, name='load_categories'),
    path('search/', views.search, name='search'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


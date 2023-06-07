from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.generic import CreateView
from main.forms import *
from main.models import *
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product

def mainpage(request):
    Products = Product.objects.all().order_by('-dateAdd')[:30]
    photos = Photo.objects.all()
    context = {
        'title': 'bazar.by - торговая площадка объявлений',
        'Products': Products,
        'photos': photos
    }
    return render(request, 'main/index.html', context)


def base(request):
    AllMainCategory = Maincategory.objects.all()
    AllCategory = Category.objects.all()
    context = {
        'AllMainCategory': AllMainCategory,
        'AllCategory': AllCategory,
    }
    return render(request, 'base.html', context)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "main/register.html"
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'main/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')


def profile(request):
    products = Product.objects.filter(user_id=request.user.id)
    AllUserInfo = User.objects.filter(id=request.user.id)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect(to='profile')
    else:
        user_form = UpdateUserForm(instance=request.user)

    context = {
        'Products': products,
        'title': 'Профиль',
        'AllUserInfo': AllUserInfo,
        'user_form': user_form
    }
    return render(request, 'main/profile.html', context)


def ProductPage(request, id):
    product = get_object_or_404(Product, pk=id)
    photos = Photo.objects.filter(product_id=id)
    carts = Cart.objects.all()
    if request.user.is_authenticated:
        carts = Cart.objects.filter(Product=id, user=request.user)
    print(carts)
    post = Product.objects.get(id=id)
    post.update_views()

    context = {
        'title': product,
        'product': product,
        'photos': photos,
        'carts': carts
    }
    return render(request, 'main/productcard.html', context)



def categorys(request, id):
    category = get_object_or_404(Category, pk=id)
    allProducts = Product.objects.filter(category=category.id)
    return render(request, 'main/category.html', {"title":category, 'allProducts':allProducts})

def special(request):
    SpecialProducts = Product.objects.exclude(costwithdiscount=None).order_by('-views')
    return render(request, 'main/special.html', {"title":"Специальные предложения", 'SpecialProducts':SpecialProducts})


@login_required
@ensure_csrf_cookie
def toggle_favorite(request):
    product_id = request.POST.get('product_id')
    user = request.user

    try:
        cart_item = Cart.objects.get(user=user, Product_id=product_id)
        cart_item.delete()
        message = 'removed'
    except Cart.DoesNotExist:
        cart_item = Cart(user=user, Product_id=product_id)
        cart_item.save()
        message = 'added'

    response = {'message': message}
    return JsonResponse(response)




def CartPage(request):
    carts = Cart.objects.all()
    countincart = 0
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user)
        countincart = carts.count()
    return render(request,'main/cart.html', {'title':'Корзина', 'carts':carts, 'countincart': countincart})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            form.save_m2m()  # Сохранение связанных данных, например, категорий
            return redirect('home')  # Перенаправление на главную страницу после успешного добавления
    else:
        form = ProductForm()
    return render(request, 'main/add_product.html', {'form': form})


def load_categories(request):
    maincategory_id = request.GET.get('maincategoryName_id')
    categories = Category.objects.filter(maincategoryName_id=maincategory_id)
    category_options = [(category.id, category.categoryName) for category in categories]
    return JsonResponse({'categories': category_options})

def search(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    quality = request.GET.get('quality')
    is_exchange = request.GET.get('is_exchange')
    products = Product.objects.all()
    has_photo = request.GET.get('has_photo')
    sort = request.GET.get('sort')
    print('query:', query)
    if is_exchange:
        products = products.filter(is_exchange=True)

    if quality:
        products = products.filter(quality=quality)

    if query:
        products = products.filter(Q(name__icontains=query.lower()))
    if min_price:
        products = products.filter(cost__gte=min_price)

    if max_price:
        products = products.filter(cost__lte=max_price)

    if has_photo:
        product_ids_with_photo = Photo.objects.values_list('product_id', flat=True).distinct()
        products = products.filter(id__in=product_ids_with_photo)

    if sort == 'newest':
        products = products.order_by('-dateAdd')
    elif sort == 'cheapest':
        products = products.order_by('cost')
    elif sort == 'expensive':
        products = products.order_by('-cost')
    if query is "":
        products = ""
        query = ""
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'main/search.html', context)
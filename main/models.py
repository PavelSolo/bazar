from datetime import date
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.urls import reverse
from bazar import settings


class City(models.Model):
    city = models.CharField(verbose_name='Город', blank=True, max_length=300)

    def __str__(self):
        return str(self.city)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class User(AbstractUser):
    username = models.CharField(default="123", max_length=255)
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=255,
        unique=True,
    )
    phonenumber = models.CharField(verbose_name="Номер телефона", blank=True, max_length=13, validators=[RegexValidator(r'^(\+375|80)(29|25|44|33)(\d{3})(\d{2})(\d{2})$')])
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, verbose_name="Город")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Maincategory(models.Model):
    maincategoryName = models.CharField(verbose_name='Название основной категории', max_length=50, unique=True)

    def __str__(self):
        return str(self.maincategoryName)

    class Meta:
        verbose_name = "Основная категория"
        verbose_name_plural = "Основные категории"


class Category(models.Model):
    maincategoryName = models.ForeignKey(Maincategory, on_delete=models.CASCADE, null=False, verbose_name="Главная категория")
    categoryName = models.CharField(verbose_name='Подкатегория', max_length=50, unique=True)

    def __str__(self):
        return str(self.categoryName)

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


class Product(models.Model):
    QUALITY_CHOICES = (
        ('new', 'Новое'),
        ('used', 'Б/У'),
    )
    name = models.CharField(verbose_name='Название', unique=False, max_length=50)
    cost = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, verbose_name="Подкатегория")
    description = models.TextField(verbose_name='Описание', blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, verbose_name="Город")
    views = models.BigIntegerField(verbose_name="Количество просмотров", default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    dateAdd = models.DateTimeField('Дата добавления', default=timezone.now)
    visible_phone = models.BooleanField('Видимость номера')
    quality = models.CharField(max_length=4, choices=QUALITY_CHOICES)
    is_exchange = models.BooleanField('Возможен обмен')
    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('product', kwargs={"id": self.id})

    def update_views(self, *args, **kwargs):
        self.views = self.views + 1
        super(Product, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering=['name']


class Photo(models.Model):
    photo = models.ImageField(verbose_name='Фото', upload_to="img/", blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True,verbose_name="Товар")

    def __str__(self):
        return str(self.product) + "(" + str(self.photo)+")"

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    Product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    dateAdd = models.DateField('Дата добавления', default=date.today)

    def __str__(self):
        return str(self.user)+" "+str(self.Product)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        unique_together = ('user', 'Product')



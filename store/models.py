from django.forms.models import ModelMultipleChoiceField
from accounts.models import Account
from django.db.models.deletion import CASCADE
from category.models import Category
from django.db import models
from category.models import Category
from django.urls import reverse
from django.db.models import Avg


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.product_name


    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])


    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0

        if reviews['average'] is not None:
            avg = float(reviews['average'])

        return avg


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(
            variation_category='color', 
            is_active=True
        )

    
    def sizes(self):
        return super(VariationManager, self).filter(
            variation_category='size', 
            is_active=True,
        )


variation_category_choices = (
    ('color', 'Cor'),
    ('size', 'Tamanho'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self) -> str:
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products/', max_length=255)

    class Meta:
        verbose_name = "Galeria do Produto"
        verbose_name_plural = "Galerias dos Produtos"

    def __str__(self) -> str:
        return self.product.product_name
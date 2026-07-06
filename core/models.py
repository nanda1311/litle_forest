from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field


# ================== COMMON CHOICES ==================
STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)


# ================== USER RELATED ==================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    # Optional profile image for address
    profile_image = models.ImageField(upload_to='address_images/', null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.city}, {self.country}'


# ================== PRODUCTS ==================
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name
class Product(models.Model):

    PRODUCT_TYPES = (
        ('bonsai', 'Bonsai'),
        ('terrarium', 'Terrarium'),
    )

    name = models.CharField(max_length=200)

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES,
        default='bonsai'
    )

    description = CKEditor5Field(
        'Description',
        config_name='extends',
        blank=True,
        null=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    category = models.ForeignKey(
        'Category',
        related_name='products',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    discount_percentage = models.PositiveIntegerField(blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    
    availability = models.BooleanField(default=True)   # False = sold out (shown faded)
    is_active = models.BooleanField(default=True)      # False = completely hidden from site
    
    delivery_date = models.DateField(blank=True, null=True)
    sku = models.CharField(max_length=100, blank=True, null=True)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    height = models.CharField(max_length=50, blank=True, null=True)

    reviews_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0, blank=True, null=True)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.stock_quantity <= 5

    def is_sold_out(self):
        return not self.availability   # sold out when availability is False

    def calculate_discount_percentage(self):
        if self.price and self.discounted_price:
            return int(100 - ((self.discounted_price / self.price) * 100))
        return 0

    def save(self, *args, **kwargs):
        if self.price and self.discounted_price:
            self.discount_percentage = self.calculate_discount_percentage()
        else:
            self.discount_percentage = 0
        super().save(*args, **kwargs)

    
    is_featured = models.BooleanField(
        default=False,
        help_text="Show this product in the 'Latest Products' section on the homepage"
    )
    featured_at = models.DateTimeField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if self.price and self.discounted_price:
            self.discount_percentage = self.calculate_discount_percentage()
        else:
            self.discount_percentage = 0

        # Stamp/clear featured_at based on the flag
        if self.is_featured:
            if not self.featured_at:
                self.featured_at = timezone.now()
        else:
            self.featured_at = None

        super().save(*args, **kwargs)

        if self.is_featured and self.category_id:
            self._enforce_featured_limit()

    def _enforce_featured_limit(self, limit=6):
        """Keep at most `limit` featured products per category.
        If exceeded, un-feature the oldest ones first."""
        others = Product.objects.filter(
            category_id=self.category_id,
            is_featured=True
        ).exclude(pk=self.pk).order_by('featured_at')

        excess = others.count() - (limit - 1)
        if excess > 0:
            oldest_ids = list(others.values_list('pk', flat=True)[:excess])
            Product.objects.filter(pk__in=oldest_ids).update(
                is_featured=False, featured_at=None
            )


class ProductImage(models.Model):
    image = models.ImageField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.product:
            return f"{self.product.name} Thumbnail"
        return "Orphan Thumbnail"



# ================== CART & WISHLIST ==================
class MyCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Cart for {self.user.username}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ================== ORDERS ==================
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Completed, Canceled
    payment_status = models.CharField(max_length=20, default='Unpaid')  # Unpaid, Paid, Refunded
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    items = models.ManyToManyField('Product', through='OrderItem', related_name='orders')
    address = models.ForeignKey('Address', on_delete=models.CASCADE, null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# ================== BLOG ==================
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="blog/")
    content = CKEditor5Field("Content", config_name="extends", blank=True, null=True)
    date = models.DateField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1

            while BlogPost.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ================== CONTACT & MISC ==================
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"
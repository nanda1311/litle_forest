from django.contrib import admin
from .models import *


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discounted_price', 'stock_quantity',
                     'availability', 'is_active', 'is_featured']
    list_editable = ['availability', 'is_active', 'is_featured']
    list_filter = ['is_active', 'availability', 'is_featured', 'product_type', 'category']
    search_fields = ['name', 'sku']

admin.site.register(Category)
admin.site.register(BlogPost)
admin.site.register(MyCart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ContactMessage)
admin.site.register(ProductImage)
admin.site.register(Wishlist)
admin.site.register(Address)
from django.contrib import admin
from .models import *

# Register existing models
admin.site.register(Category)
admin.site.register(BlogPost)
admin.site.register(MyCart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(TerrariumProduct)
admin.site.register(ContactMessage)

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Wishlist)

admin.site.register(Address)

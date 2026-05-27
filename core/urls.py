from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import *
from core import views

urlpatterns = [

    # CKEDITOR
    path("ckeditor5/", include("django_ckeditor_5.urls")),

    # ================= MAIN PAGES =================
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('contact/', contact, name='contact'),
    path('terrarium/', views.terrarium_page, name='terrarium_page'),
    path('base/', base, name='base'),
    path('check-delivery/',views.check_delivery,name='check_delivery'),

    # ================= AUTH =================
    path('loginaccount/', loginaccount, name='loginaccount'),
    path('createaccount/', createaccount, name='createaccount'),
    path("login/", auth_views.LoginView.as_view(template_name="dashboard/login.html"), name="login"),
    path('logout/', logout, name='logout'),

    # ================= CART =================
    path('cart/', cart, name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<str:pk>/', increase_quantity, name='increase_quantity'),
    path('cart/decrease/<str:pk>/', decrease_quantity, name='decrease_quantity'),
    path('update-cart/<int:product_id>/', update_cart, name='update_cart'),
    path('clear-cart/', clear_cart, name='clear_cart'),

    # ================= WISHLIST =================
    path('wishlist/', wishlistproduct, name='wishlistproduct'),
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('clear_wishlist/', clear_wishlist, name='clear_wishlist'),
    path("move-to-cart/<int:product_id>/", move_to_cart, name="move_to_cart"),

    # ================= PRODUCTS =================
    path('collection/', collection, name='collection'),
    path('collection/<int:category_id>/', collection, name='collection_by_category'),
    path('categories/<str:pk>/', categories, name='categories'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),

    # ================= ORDERS =================
    path('create-order/', create_order, name='create-order'),
    path('order-complete/', order_complete, name='order_complete'),
    path('order-failure/', order_failure, name='order_failure'),
    path('ordercompleted/', ordercompleted, name='ordercompleted'),
    path('orderhistory/', orderhistory, name='orderhistory'),
    path('orderhistory/<int:order_id>/', order_history_detail, name='orderhistory'),

    # ================= PAYMENT =================
    path('payment/verify/', payment_verify, name='payment_verify'),

    # ================= PROFILE =================
    path('profile/', profile, name='profile'),
    path('proaddress', proaddress, name='proaddress'),
    path('changepassword', changepassword, name='changepassword'),
    path('edit-address/<int:pk>/', edit_address, name='edit_address'),
    path('delete-address/<int:pk>/', delete_address, name='delete_address'),

    # ================= EXTRA =================
    path('faq/', Faq, name='faq'),
    path('cartempty/', cartempty, name='cartempty'),
    path('privacypolicy/', privacypolicy, name='privacypolicy'),
    path('paymentpolicy/', paymentpolicy, name='paymentpolicy'),
    path('termscondition/', termscondition, name='termscondition'),
    path('returnpolicy/', returnpolicy, name='returnpolicy'),
    path('comingsoon/', comingsoon, name='comingsoon'),
    path('checklist/', checklist, name='checklist'),
    path('buy-now/<int:product_id>/', buy_now, name='buy_now'),

    # ================= BLOG =================
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),

    # ================= DASHBOARD =================
    path("dashboard/", dashboard, name="dashboard"),

    # PRODUCTS
    path('dashboard/products/', product_list, name='product_list'),
    path('dashboard/products/add/', product_create, name='product_create'),
    path('dashboard/products/edit/<int:pk>/', product_update, name='product_update'),
    path('dashboard/products/delete/<int:pk>/', product_delete, name='product_delete'),

    # BLOGS
    path('dashboard/blogs/', blog_list, name='blog_list'),
    path('dashboard/blogs/add/', blog_create, name='blog_create'),
    path('dashboard/blogs/edit/<int:pk>/', blog_update, name='blog_update'),
    path('dashboard/blogs/delete/<int:pk>/', blog_delete, name='blog_delete'),

    # CATEGORIES
    path('dashboard/categories/', category_list, name='category_list'),
    path('dashboard/categories/add/', category_create, name='category_create'),
    path('dashboard/categories/edit/<int:pk>/', category_update, name='category_update'),
    path('dashboard/categories/delete/<int:pk>/', category_delete, name='category_delete'),

    # ORDERS
    path('dashboard/orders/', order_list, name='order_list'),
    path('dashboard/orders/<int:order_id>/', order_detail, name='order_detail'),

    # CUSTOMERS
    path('dashboard/customers/', customer_list, name='customer_list'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
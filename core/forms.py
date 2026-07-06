from django import forms
from .models import Product, BlogPost, Category


# =============================
# PRODUCT FORM
# =============================


from django import forms
from .models import Product



class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['reviews_count', 'discount_percentage', 'rating','featured_at']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'height': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discounted_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
# BLOG FORM
# =============================


class SignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name', 'required': 'required'})
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username', 'required': 'required'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address', 'required': 'required'})
    )
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number', 'required': 'required'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a password', 'required': 'required'})
    )
  
    terms = forms.BooleanField(
        required=True,
        label="I have read and agree with the terms & condition"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 10 or not phone.startswith(('6','7','8','9')):
            raise forms.ValidationError("Enter valid 10 digit phone number starting with 6-9")
        return phone

class BlogForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

# =============================
# CATEGORY FORM
# =============================

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        
        
from django import forms
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = "__all__"
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})
        }
        
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "image", "status"]
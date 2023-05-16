from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from taggit.managers import TaggableManager
from taggit.models import Tag
from PIL import Image
from django.db.models.signals import post_save
from django.db.models import Avg
from django.utils.html import format_html

STATUS_CHOICE =(
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
)

STATUS =(
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)

RATING =(
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)

PAYMENT_METHOD = (
    ("cod", "Cash on delivery"),
    ("paypal", "Paypal Payment")
)






def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Tags(models.Model):
    pass

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="Category")

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50"/>'% (self.image.url))
    
    def __str__(self):
        return self.title
    
class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=100, default="123 main street")
    contact = models.CharField(max_length=100, default="+92 312 1234567")
    chat_resp_time = models.CharField(max_length=100, default="100")
    shipping_on_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    image = models.ImageField(upload_to=user_directory_path)
    description = models.TextField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    avr_rating = models.FloatField(null=True)
    class Meta:
        verbose_name_plural = "Vendors"

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50"/>'% (self.image.url))
    
    def __str__(self):
        return self.title
    
   
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=30, alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Fresh product")
    image = models.ImageField(upload_to=user_directory_path, default="product.jpg")
    description = RichTextUploadingField(null=True, blank=True, default="This is the Product")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="vendorproducts")
    price = models.DecimalField(max_digits=999999, decimal_places=2, default="100")
    old_price = models.DecimalField(max_digits=999999, decimal_places=2, default="200")
    tags = TaggableManager(blank=True)
    days_return = models.CharField(max_length=100, null=True, default="100")
    warranty_period = models.CharField(max_length=100, null=True, default="100")
    specification = RichTextUploadingField(null=True, blank=True)
    #tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)
    product_status = models.CharField(choices=STATUS, max_length=10, default="published")

    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=True)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=5, max_length=10, alphabet="1234567890")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50"/>'% (self.image.url))
    
    def __str__(self):
        return self.title
    
    def get_percentage(self):
        new_price = ((self.old_price-self.price) / self.old_price) * 100
        return new_price
 
    def get_average_rating(self):
        return self.reviews.aggregate(rating=Avg('rating'))['rating']
    
    

    
class ProductImages(models.Model):
    Images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images" ,on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Product Images"



##################################### Cart, Order, OrderItems and Addres #############################################
##################################### Cart, Order, OrderItems and Addres #############################################
##################################### Cart, Order, OrderItems and Addres #############################################
##################################### Cart, Order, OrderItems and Addres #############################################

class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=999999, decimal_places=2, default="100")
    paid_status = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=255, null=True, default="cod")

    class Meta:
        verbose_name_plural = "Cart Orders"

class CartOrderItems(models.Model):
    
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=999999, decimal_places=2, default="100")
    total = models.DecimalField(max_digits=999999, decimal_places=2, default="100")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Cart Order Items"

    def order_img(self):
        return mark_safe('<img src="%s" width="50" height="50"/>'% (self.image))
    
################################### Product Review, wishlist, Address ###################################################

class wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return self.product.title

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    postal_code = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=200, null=True)
    
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Address"

class ContactUs(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name_plural = "Contact Us"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to="Users_Profile_image")

    def __str__(self):
        return self.first_name
    
    class Meta:
        verbose_name_plural = "Users_Profile"

    def profile_image(self):
        return mark_safe('<img src="%s" width="50" height="50"/>'% (self.image.url))
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

class VendorNotification(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()



class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title

    def get_rating(self):
        return self.rating
    
from django.contrib import admin
from core.models import Product, ContactUs, Notification, VendorNotification, UserProfile, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist, Address

class ProductImagesAdmin(admin.TabularInline):
    model = ProductImages

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin]
    list_display = ['title', 'product_image', 'user', 'pid', 'category', 'vendor', 'price','featured', 'product_status']    

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']    

class VendorAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor_image'] 

class CartOrderAdmin(admin.ModelAdmin):
    list_editable = ['paid_status', 'product_status']
    list_display = ['user', 'price', 'paid_status', 'order_date', 'product_status', 'payment_method']

class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'invoice_no', 'item', 'order_img', 'qty', 'price', 'total']

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']

class wishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'date']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'country', 'city', 'mobile', 'status']

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'bio']

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'cart_order', 'message']

class VendorNotificationAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'created_at', 'message']


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItems, CartOrderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(wishlist, wishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(VendorNotification, VendorNotificationAdmin)


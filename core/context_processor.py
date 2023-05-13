from core.models import Product, UserProfile,Notification, VendorNotification ,Category, Vendor,Tags, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist, Address
from django.db.models import Min, Max, Avg
from django.contrib import messages
from userauths.models import User
from taggit.models import Tag
from django.http import HttpRequest, JsonResponse

def default(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    vendor_list = Vendor.objects.all()
    profile_image = None
    vendor_image = None
    if request.user.is_authenticated and UserProfile.objects.filter(user=request.user).exists():
        profile_image = UserProfile.objects.get(user = request.user)
    if request.user.is_authenticated and UserProfile.objects.filter(user=request.user).exists and request.user.is_vendor == True:    
        vendor_image = Vendor.objects.get(user = request.user)

    for vendor in vendor_list:
        avg_rating = ProductReview.objects.filter(product__vendor=vendor).aggregate(avg_rating=Avg('rating'))['avg_rating']
        vendor.avr_rating = avg_rating

    tags = Tag.objects.all()
    noti = []
    if request.user.is_authenticated:
        noti = Notification.objects.filter(user=request.user).order_by("-id")
    unread_noti = []
    if request.user.is_authenticated:
        unread_noti = Notification.objects.filter(user=request.user, is_read=False).order_by("-id")
    ven_noti = []
    if request.user.is_authenticated:
        ven_noti =  VendorNotification.objects.filter(vendor__user=request.user).order_by("-id")
    unread_ven_noti = []
    if request.user.is_authenticated:
        unread_ven_noti =  VendorNotification.objects.filter(vendor__user=request.user, is_read=False).order_by("-id")
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))
    try:
        address = Address.objects.get(user=request.user)
    except:
        address = None

    try:
        wishlist_count = wishlist.objects.filter( user = request.user)
    except:
        wishlist_count = 0
    return{
        "categories": categories,
        "address": address,
        "vendor_list": vendor_list, 
        "min_max_price": min_max_price,
        "wishlist_count": wishlist_count,
        "tags": tags,
        "products": products,
        "noti": noti,
        "ven_noti": ven_noti,
        "unread_noti": unread_noti,
        "unread_ven_noti": unread_ven_noti,
        "profile_image": profile_image,
        "vendor_image": vendor_image,
    }


import re
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg, Sum
from userauths.models import User
from core.models import Product, ContactUs, Notification, Category, VendorNotification, Vendor, UserProfile, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist, Address
from taggit.models import Tag
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail 
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from requests import session 
from django.contrib.auth.decorators import login_required
from django.core import serializers
import calendar
from django.db.models.functions import ExtractMonth
from datetime import datetime

# Create your views here.

def index(request):
    
    latest_products = Product.objects.filter(product_status="published",featured=True).order_by('-id')
    most_rated_products = Product.objects.annotate(rating=Avg('reviews__rating')).order_by('-rating')
   
    

    context= {
        "latest_products":latest_products,
        "most_rated_products": most_rated_products,
       
    }

    return render(request, "core/index.html", context)

def product_list_view(request):
    product = Product.objects.filter(product_status="published",featured=True)
    context= {
        "products":product,
    }

    return render(request, "core/product-list.html", context)

def category_list_view(request):
    categories = Category.objects.all()
    context= {
        "categories": categories
    }
    return render(request, "core/category-list.html", context)

def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context={
        "category":category,
        "products":products
    }
    return render(request, "core/category-product-list.html", context)

def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context={
        "vendors": vendors
    }
    return render(request, "core/vendor-list.html", context)

def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    product = Product.objects.filter(vendor=vendor, product_status="published")
    average_rating = ProductReview.objects.filter(product__vendor__vid=vendor.vid).aggregate(avg_rating=Avg('rating'))['avg_rating']
    context={
        "vendor": vendor,
        "product": product,
        "average_rating": average_rating,
    }
    return render(request, "core/vendor-detail.html", context)

def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    related_products = Product.objects.filter(category=product.category).exclude(pid=pid)
    p_image = product.p_images.all()
    reviews = ProductReview.objects.filter(product=product)
    vendor_average_rating = ProductReview.objects.filter(product__vendor__vid=product.vendor.vid).aggregate(avg_rating=Avg('rating'))['avg_rating']
    vendor_rating = vendor_average_rating*20
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    review_form = ProductReviewForm()
    
    make_review= True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count>0:
            make_review=False

    context={
        "product": product,
        "make_review": make_review,
        "p_image": p_image,
        "average_rating": average_rating,
        "related_products": related_products,
        "reviews": reviews,
        "review_form": review_form,
        "vendor_average_rating": vendor_average_rating,
        "vendor_rating": vendor_rating
        
    }
    return render(request, "core/product-detail.html", context)

def tag_list(request, tag_slug = None):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context= {
        "products": products,
        "tag": tag
    }
    return render(request, "core/tag.html" ,context)

def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user=request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],

    )
    context = {
        'user':user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))
    
    return JsonResponse(
        {
            'bool': True,
            'context': context,
            'average_reviews': average_reviews
            }
    )

def search_view(request):
    query = request.GET.get("q")
    products = Product.objects.filter(title__icontains=query).order_by("-date")
    context={
        "products":products,
        "query":query,
    }
    return render(request, "core/search.html" ,context)

def filter_product(request):
    categories= request.GET.getlist("category[]")
    vendors= request.GET.getlist("vendor[]")
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(product_status = "published").order_by("-id").distinct()
    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)
  
    if len(categories)>0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors)>0:
        products = products.filter(vendor__id__in=vendors).distinct()

    context= {
        "products": products
    }

    data = render_to_string("core/async/product-list.html", context)
    return JsonResponse({"data": data})

def add_to_cart(request):
    cart_product = {}
    cart_product[request.GET.get('id')] = {
        "title": request.GET.get('title'),
        "qty": request.GET.get('qty'),
        "price": request.GET.get('price'),
        "image": request.GET.get('image'),
        "pid": request.GET.get('pid'),
    }
    if 'cart_data_obj' in request.session:
        if request.GET.get('id') in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[request.GET.get('id')]['qty'] = int(cart_product[request.GET.get('id')]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj']= cart_data
    else:
        request.session['cart_data_obj']= cart_product
    return JsonResponse({"data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})

def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("/")
    
def delete_item_from_cart(request):
    product_id = str(request.GET.get('id'))
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data=request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj']=cart_data
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

def update_from_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data=request.session['cart_data_obj']
            cart_data[str(request.GET["id"])]['qty']=product_qty
            request.session['cart_data_obj']=cart_data
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})

@login_required
def checkout_view(request):
    if 'cart_data_obj' in request.session:
        address = Address.objects.filter(user=request.user)
        context={
            'address':address,
        }
        
        cart_total_amount = 0
        if 'cart_data_obj' in request.session:
            for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])
            return render(request, "core/checkout.html", {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
    else:
        messages.warning(request,"Your cart is empty")
        return redirect("/")
@login_required
def paypal_view(request):
    
    cart_total_amount = 0
    total_amount = 0
    if 'cart_data_obj' in request.session:
        #total amount for the paypal
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])
        order = CartOrder.objects.create(
            user = request.user,
            price = total_amount,
            payment_method='paypal',
            paid_status = True,
        )
        Notification.objects.create(
            user=request.user,
            cart_order = order,
            message=f"Hey {request.user} Your order was placed."
        )
        # Send email to the user
        subject = 'Order Confirmation'
        message = f"Dear {request.user},\n\nWe are thrilled to inform you that your order has been placed successfully. Here are the details of your purchase:\n\nOrder ID: {order.id}\nTotal Price: {order.price}\nPayment Method: Cash on Delivery\n\nYour order will be delivered to the following address:\n{address.address}\n{address.city}, {address.country}\n\nTo view your order details, please visit our website. If you have any questions or concerns, please don't hesitate to contact us.\n\nThank you for shopping at Shaheer Mart!\n\nBest regards,\nShaheer Mart Customer Service"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [request.user.email,]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
        #total amount for the cart total
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            product = Product.objects.get(pid = item['pid'])
            cart_order_products = CartOrderItems.objects.create(
                order=order,
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                invoice_no="INVOICE-NO"+str(order.id),
                price=item['price'],
                total = float(item['qty'])*float(item['price']),
                product=product

            )
            vendor = Vendor.objects.get(vid=product.vendor.vid)
            VendorNotification.objects.create(
                vendor=vendor,
                message = f"Hey! You got an order from {request.user}, Product:{item['title']} quantity:{item['qty']}."
            )
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("/")
        

    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': cart_total_amount,
        'item_name': "Order-Item-No-"+str(order.id),
        'invoice': "INV_NO-"+str(order.id),
        'currency_code': "USD",
        'notify_url': "http://{}{}".format(host, reverse("paypal-ipn")),
        'return_url': "http://{}{}".format(host, reverse("payment-completed")),
        'cancel_url': "http://{}{}".format(host, reverse("payment-failed")),
    }
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
    cart_total_amount = 0
 
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/paypal.html",  {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount, 'paypal_payment_button':paypal_payment_button})




@login_required
def cash_on_delivery_view(request):
    if 'cart_data_obj' in request.session:
        total_amount = 0
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])
        print("creating order")
        order = CartOrder.objects.create(
            user=request.user,
            price=total_amount,
            payment_method='cod',
            paid_status= False,
        )
        
        for p_id, item in request.session['cart_data_obj'].items():
            product = Product.objects.get(pid = item['pid'])
            cart_order_products = CartOrderItems.objects.create(
                order=order,
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                invoice_no="INVOICE-NO"+str(order.id),
                price=item['price'],
                total=float(item['qty'])*float(item['price']),
                product = product,
            )
            vendor = Vendor.objects.get(vid=product.vendor.vid)
            VendorNotification.objects.create(
                vendor=vendor,
                message = f"Hey! You got an order from {request.user}, Product:{item['title']} quantity:{item['qty']}."
            )
        address = Address.objects.get(user=request.user)
        # Send email to the user
        subject = 'Order Confirmation'
        message = f"Dear {request.user},\n\nWe are thrilled to inform you that your order has been placed successfully. Here are the details of your purchase:\n\nOrder ID: {order.id}\nTotal Price: {order.price}\nPayment Method: Cash on Delivery\n\nYour order will be delivered to the following address:\n{address.address}\n{address.city}, {address.country}\n\nTo view your order details, please visit our website. If you have any questions or concerns, please don't hesitate to contact us.\n\nThank you for shopping at Shaheer Mart!\n\nBest regards,\nShaheer Mart Customer Service"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [request.user.email,]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
        Notification.objects.create(
            user=request.user,
            cart_order = order,
            message=f"Hey {request.user} Your order was placed."
        )
        messages.success(request, "Your order has been placed successfully.")
        return redirect("payment-completed")
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("/")


@login_required
def payment_completed_view(request):
    address = Address.objects.get(user=request.user)
    now = datetime.now()
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("/")

    return render(request, 'core/payment-completed.html', {"cart_data":request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount, 'address': address, "now":now})
@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')

@login_required
def dashboard(request):
    orders = CartOrder.objects.filter(user=request.user).annotate(month=ExtractMonth("order_date")).values("month").annotate(count=Count("id")).values("month", "count")
    no_of_orders = CartOrder.objects.filter(user=request.user).annotate(Count("id"))
    in_process = CartOrder.objects.filter(user=request.user).filter(product_status = "processing")
    delivered = CartOrder.objects.filter(user=request.user).filter(product_status = "delivered")
    month = []
    total_orders = []
    for i in orders:
        month.append(calendar.month_name[i["month"]])
        total_orders.append(i["count"])
    context ={
        "orders": orders,
        "month": month,
        "total_orders": total_orders,
        "no_of_orders": no_of_orders,
        "in_process": in_process,
        "delivered": delivered,
    }
    return render(request, "core/dashboard.html", context)

@login_required
def order(request):
    orders= CartOrder.objects.filter(user=request.user, payment_method = "cod").order_by('-id')
    context={
        "orders":orders,
    }
    return render(request, "core/order.html", context)

@login_required
def order_detail(request, id):
    order= CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItems.objects.filter(order=order)
    context={
        "order_items":order_items,
    }
    return render(request, "core/order-detail.html", context)

@login_required
def profile(request):
    address = Address.objects.filter(user=request.user)
    profile = UserProfile.objects.filter(user=request.user)

    context={
        "profile": profile,
        'address': address,
    }
    return render(request, "core/profile.html",context)

@login_required
def address(request):
    address = Address.objects.filter(user=request.user)
    profile = UserProfile.objects.filter(user=request.user)

    context={
        "profile": profile,
        'address': address,
    }
    return render(request, "core/address.html",context)

@login_required
def update_address(request):
    address = Address.objects.filter(user=request.user)

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        city = request.POST.get("city")
        country = request.POST.get("country")
        postal_code = request.POST.get("postal_code")

        new_address = Address.objects.get(user=request.user)
        new_address.address = address
        new_address.mobile = mobile
        new_address.city = city
        new_address.country = country
        new_address.postal_code = postal_code
        new_address.save()
        messages.success(request, "Address updated successfully")
        previous_url = request.POST.get('previous_url', '/')
        return redirect(previous_url)
    context={
        'address': address,
    }
    return render(request, "core/update-address.html",context)
@login_required
def wishlist_view(request):
    try:
        wish_list = wishlist.objects.filter(user=request.user)
    except:
        wish_list = None
    context = {
        "w":wish_list
    }
    return render(request, "core/wishlist.html", context)

def add_to_wishlist(request):
    id = request.GET['id']
    product = Product.objects.get(id=id)
    context={}
    wishlist_count = wishlist.objects.filter(product = product, user = request.user).count()

    if wishlist_count>0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = wishlist.objects.create(
            product=product,
            user=request.user
        )
        context = {
            "bool": True
        }
    return JsonResponse(context)

def remove_from_wishlist(request):
    pid = request.GET['id']
    wish_list = wishlist.objects.filter(user=request.user)
    product = wishlist.objects.get(id = pid)
    product.delete()

    context={
        "bool": True,
        "wishlist": wish_list,
    }
    wishlist_json = serializers.serialize("json", wish_list)
    data = render_to_string("core/async/wishlist-list.html", context)
    return JsonResponse({"data":data, "wishlist":wishlist_json })

def contact_view(request):
    return render(request, "core/contactus.html")


def contact_ajax(request):
    full_name = request.GET['full_name']
    email = request.GET["email"]
    phone = request.GET["phone"]
    message = request.GET["message"]

    new_message = ContactUs.objects.create(
        full_name = full_name,
        email = email,
        phone = phone,
        message = message,
    )
    data = {
        "bool": True,
        "message": "Message sent Successfully"
    }
    return JsonResponse({"data":data})

@login_required
def update_profile(request):

    profile = UserProfile.objects.filter(user=request.user)
    context = {
        "profile": profile,
    }
    if request.method == 'POST':
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        image = request.FILES.get('image')

        
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.bio = bio
        user_profile.image = image or user_profile.image
        user_profile.save()


        messages.success(request, 'Profile was updated successfully!')
        return redirect('profile')
    
    return render(request, 'core/update-profile.html', context)

@login_required
def create_profile(request):
    if UserProfile.objects.filter(user=request.user).exists():
        messages.warning(request, 'Profile is already created!')
        return redirect('/')
    profile = UserProfile.objects.filter(user=request.user)
    context = {
        "profile": profile,
    }
    if request.method == 'POST':
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        image = request.FILES.get('image')

        
        user_profile = UserProfile.objects.create(
            user=request.user,
            first_name = first_name,
            last_name = last_name,
            bio = bio,
            image = image
            )
        user_profile.save()

        return redirect('add-address')
    
    return render(request, 'core/create-profile.html', context)

@login_required
def add_address(request):
    address = Address.objects.filter(user=request.user)
    if Address.objects.filter(user=request.user).exists():
        messages.warning(request, 'Address has already been added!')
        return redirect('/')

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")
        city = request.POST.get("city")
        country = request.POST.get("country")
        postal_code = request.POST.get("postal_code")

        new_address = Address.objects.create(
            user=request.user,
            address = address,
            mobile = mobile,
            city = city,
            country = country,
            postal_code = postal_code,

        )
        new_address.save()
        messages.success(request, "Profile created Successfully")
        return redirect("/")
    context={
        'address': address,
    }
    return render(request, "core/add-address.html", context)

@login_required
def vendor_profile(request):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, 'Please create your Store!')
        return redirect('create-vendor-profile')
    
    vendor = Vendor.objects.filter(user=request.user)
    context = {
        "vendor":vendor,
    }

    return render(request, "core/vendor-profile.html", context)

@login_required
def create_vendor_profile(request):
    if Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You can't create more than one Store!")
        return redirect('/')
    return render(request, "core/create-vendor-profile.html")

@login_required
def create_store(request):
    if Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You can't create more than one store!")
        return redirect('/')
    if request.method == "POST":
        title = request.POST.get("title")
        address = request.POST.get("address")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        contact = request.POST.get("contact")

        new_vendor = Vendor.objects.create(
            user=request.user,
            title = title,
            address = address,
            image = image,
            description = description,
            contact = contact,
        )
        new_vendor.save()
        user1 = User.objects.get(username=request.user.username)
        user1.is_vendor = True
        user1.save()

        messages.success(request, "Congratulations! You are now a Seller.")
        return redirect("/")
    
    return render(request, "core/create-store.html")


@login_required
def update_store(request):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You first need to create your Store")
        return redirect('create-vendor-profile')
    vendor = Vendor.objects.filter(user=request.user)
    context ={
        "vendor": vendor,
    }
    if request.method == "POST":
        title = request.POST.get("title")
        address = request.POST.get("address")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        contact = request.POST.get("contact")

        new_vendor = Vendor.objects.get(user=request.user)
        new_vendor.title = title
        new_vendor.address = address
        new_vendor.image = image or new_vendor.image
        new_vendor.description = description
        new_vendor.contact = contact
        
        new_vendor.save()

        messages.success(request, "Store was updated.")
        return redirect("/")
    
    return render(request, "core/update-store.html", context)

@login_required
def store_products(request):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You first need to create your Store")
        return redirect('create-vendor-profile')
    products = Product.objects.filter(user=request.user)
    context = {
        "products":products,
    }
    return render(request, "core/store-products.html", context)

@login_required
def create_products(request):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You first need to create your Store")
        return redirect('create-vendor-profile')
    vendor = Vendor.objects.get(user=request.user)
    if request.method == "POST":
        title = request.POST.get("title")
        old_price = request.POST.get("old_price")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        tags_input = request.POST.get("tags")
        if tags_input:
            tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            new_product = Product.objects.create(
                user=request.user,
                vendor=vendor,
                title=title,
                old_price=old_price,
                price=price,
                image=image,
                description=description,
                days_return=request.POST.get("days_return"),
                warranty_period=request.POST.get("warranty_period"),
                in_stock=request.POST.get("in_stock") == "on",
                specification=request.POST.get("specification"),
                category=Category.objects.get(title=request.POST.get("category")),
            )
            new_product.tags.add(*tags_list)
            for index, file in enumerate(request.FILES.getlist('images')):
                ProductImages.objects.create(
                    product=new_product,
                    Images=file,
                    )

            return redirect("store-products")
    else:
        tags_list = []
    categories = Category.objects.all()
    context = {"categories": categories, "tags_list": tags_list}
    return render(request, "core/create-products.html", context)

@login_required
def update_product(request, pid):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You first need to create your Store")
        return redirect('create-vendor-profile')
    product = Product.objects.get(pid=pid)
    vendor = Vendor.objects.get(user=request.user)
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "form1":
            product.delete()
            return redirect('store-products')
        else:
            product.title = request.POST.get("title")
            product.old_price = request.POST.get("old_price")
            product.price = request.POST.get("price")
            product.image = request.FILES.get("image") or product.image
            product.description = request.POST.get("description")
            product.days_return = request.POST.get("days_return")
            product.warranty_period = request.POST.get("warranty_period")
            product.in_stock = request.POST.get("in_stock") == "on"
            product.specification = request.POST.get("specification")
            product.category = Category.objects.get(title=request.POST.get("category"))
            product.tags.clear()
            tags_input = request.POST.get("tags")
            if tags_input:
                tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                product.tags.add(*tags_list)
            product.save()
            return redirect("store-products")
    else:
        tags_list = product.tags.all()
    categories = Category.objects.all()
    context = {
        "categories": categories, 
        "tags_list": tags_list, 
        "p": product
        }
    return render(request, "core/update-product.html", context)

@login_required
def user_notifications(request):
    notification = Notification.objects.filter(user=request.user).order_by("-id")
    for n in notification:
        n.is_read=True
        n.save()
    context = {
        "notification": notification
    }
    return render(request, "core/user-notifications.html", context)

@login_required
def vendor_notifications(request):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You first need to create your Store")
        return redirect('create-vendor-profile')
    notification = VendorNotification.objects.filter(vendor__user=request.user).order_by("-id")
    for n in notification:
        n.is_read=True
        n.save()
    context = {
        "notification": notification
    }
    return render(request, "core/vendor-notifications.html", context)

@login_required
def vendor_orders(request):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You first need to create your Store")
        return redirect('create-vendor-profile')
    vendor = Vendor.objects.get(user=request.user)
    orders = CartOrderItems.objects.filter(product__vendor=vendor, order__payment_method="cod").order_by("-id")
    context = {
        "order": orders,
    }
    return render(request, "core/vendor-orders.html", context)

def customers_profile(request, id):
    user = User.objects.get(id=id)
    profile = UserProfile.objects.get(user=user)
    address = Address.objects.get(user=user)
    context = {
        "p": profile,
        "address":address,
    }
    return render(request, "core/customer-profile.html", context)

def vendor_dashboard(request):
    if not Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You first need to create your Store")
        return redirect('create-vendor-profile')
    vendor = Vendor.objects.get(user=request.user)
    total_sum = CartOrderItems.objects.filter(product__vendor = vendor).aggregate(Sum('total'))
    total_orders = CartOrderItems.objects.filter(product__vendor = vendor)
    delivered = CartOrderItems.objects.filter(order__product_status="delivered")
    to_be_delivered = CartOrderItems.objects.filter(order__product_status="processing" or "shipped")
    total_revenue = total_sum['total__sum']

    items = CartOrderItems.objects.filter(product__vendor=vendor)
    
    # Calculate monthly revenue
    monthly_revenue = items.annotate(month=ExtractMonth("order__order_date")).values("month").annotate(total=Sum("total")).values("month", "total")

    # Extract month names and revenue totals from the data
    month_names = []
    revenue_totals = []
    for monthly_data in monthly_revenue:
        month_names.append(calendar.month_name[monthly_data["month"]])
        revenue_totals.append(float(monthly_data["total"]))

   


    context = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "delivered": delivered,
        "to_be_delivered": to_be_delivered,
        "month_names": month_names,
        "revenue_totals": revenue_totals,
    }
    return render(request, "core/vendor-dashboard.html", context) 
from django.urls import path, include
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index,name="index"),
    path('products/',views.product_list_view,name="product-list"),
    path('categories/',views.category_list_view,name="category-list"),
    path('categories/<cid>/',views.category_product_list_view,name="category-product-list"),
    path('vendors/',views.vendor_list_view,name="vendor-list"),
    path('create-vendor-profile/',views.create_vendor_profile,name="create-vendor-profile"),
    path('vendor-profile/',views.vendor_profile,name="vendor-profile"),
    path('vendors/<vid>',views.vendor_detail_view,name="vendor-detail"),
    path('products/<pid>',views.product_detail_view,name="product-detail"),
    path('products/tag/<slug:tag_slug>/',views.tag_list, name="tag"),
    path('ajax-add-review/<int:pid>/',views.ajax_add_review, name="ajax-add-review"),
    path('search/',views.search_view,name="search"),
    path('filter-product/',views.filter_product,name="filter-product"),
    path('add-to-cart/', views.add_to_cart,name="add-to-cart"),
    path('cart/', views.cart_view,name="cart"),
    path('delete-from-cart/', views.delete_item_from_cart,name="delete-from-cart"),
    path('update-cart/', views.update_from_cart,name="update-cart"),
    path('checkout/', views.checkout_view,name="checkout"),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment-completed/', views.payment_completed_view, name="payment-completed"),
    path('payment-failed/', views.payment_failed_view, name="payment-failed"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('order/', views.order, name="order"),
    path('order-detail/<int:id>/', views.order_detail, name="order-detail"),
    path('profile/', views.profile, name="profile"),
    path('address/', views.address, name="address"),
    path('update-address/', views.update_address, name="update-address"),
    path('add-address/', views.add_address, name="add-address"),
    path('update-profile/', views.update_profile, name="update-profile"),
    path('create-profile/', views.create_profile, name="create-profile"),
    path('wishlist/', views.wishlist_view, name="wishlist"),
    path('add-to-wishlist/', views.add_to_wishlist, name="add-to-wishlist"),
    path('remove-from-wishlist/', views.remove_from_wishlist, name="remove-from-wishlist"),
    path('contact/', views.contact_view, name="contact"),
    path('contact-page/', views.contact_ajax, name="contact-page"),
    path('cash-on-delivery/', views.cash_on_delivery_view, name='cash-on-delivery'),
    path('create-store/', views.create_store, name='create-store'),
    path('update-store/', views.update_store, name='update-store'),
    path('store-products/', views.store_products, name='store-products'),
    path('create-products/', views.create_products, name='create-products'),
    path('update-product/<pid>', views.update_product, name='update-product'),
    path('user-notifications/', views.user_notifications, name='user-notifications'),
    path('vendor-notifications/', views.vendor_notifications, name='vendor-notifications'),
    path('vendor-orders/', views.vendor_orders, name='vendor-orders'),
    path('customer-profile/<id>', views.customers_profile, name='customer-profile'),
    path('paypal/', views.paypal_view, name='paypal'),
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor-dashboard'),

   
    
]
    
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart, CartItem


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if product.stock < 1:
        messages.error(request, "Product is out of stock.")
        return redirect('home')

    cart_obj, created = Cart.objects.get_or_create(
        user=request.user
    )

    item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(
                request,
                "Maximum available stock reached."
            )

    return redirect('cart')


@login_required
def cart(request):
    cart_obj, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart_obj.items.select_related('product')

    total = sum(
        item.product.price * item.quantity
        for item in items
    )

    return render(
        request,
        'cart.html',
        {
            'items': items,
            'total': total
        }
    )


@login_required
def update_cart(request, item_id):
    if request.method != 'POST':
        return redirect('cart')

    cart_obj, created = Cart.objects.get_or_create(
        user=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart_obj
    )

    action = request.POST.get('action')

    if action == 'increase':
        if item.quantity < item.product.stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(
                request,
                "Maximum available stock reached."
            )

    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            messages.info(
                request,
                "Quantity cannot be less than 1."
            )

    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    if request.method != 'POST':
        return redirect('cart')

    cart_obj, created = Cart.objects.get_or_create(
        user=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart_obj
    )

    item.delete()

    messages.success(
        request,
        "Product removed from your cart."
    )

    return redirect('cart')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import Product
from recommendations.models import UserProductInteraction
from recommendations.recommendation import RecommendationModel
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    # Calculate total
    total = sum(item.total_price for item in cart_items)
    
    # Get recommendations based on cart items
    model = RecommendationModel()
    model.train()
    recommended_products = model.get_recommendations(request.user.id, top_n=4)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
        'recommended_products': recommended_products
    }
    return render(request, 'cart/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )
        
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        
        # Record interaction
        interaction, created = UserProductInteraction.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        return redirect('cart:view_cart')
    
    return redirect('products:product_list')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if request.method == 'POST':
        # Process the order
        for item in cart_items:
            # Record purchase in interaction model
            interaction, created = UserProductInteraction.objects.get_or_create(
                user=request.user,
                product=item.product
            )
            interaction.purchased = True
            interaction.save()
            
            # Update product stock
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        # Clear the cart
        cart_items.delete()
        
        return redirect('cart:checkout_success')
    
    # Calculate total
    total = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total
    }
    return render(request, 'cart/checkout.html', context)

@login_required
def checkout_success(request):
    # Get new recommendations after purchase
    model = RecommendationModel()
    model.train()
    recommended_products = model.get_recommendations(request.user.id, top_n=4)
    
    context = {
        'recommended_products': recommended_products
    }
    return render(request, 'cart/checkout_success.html', context)

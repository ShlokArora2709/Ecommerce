from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from recommendations.models import UserProductInteraction
from recommendations.recommendation import RecommendationModel
def product_list(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    
    if selected_category:
        products = Product.objects.filter(category__id=selected_category)
    else:
        products = Product.objects.all()
    
    recommended_products = []
    if request.user.is_authenticated:
        model = RecommendationModel()
        model.train()
        recommended_products = model.get_recommendations(request.user.id, top_n=4)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'recommended_products': recommended_products
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Record user interaction for logged in users
    if request.user.is_authenticated:
        interaction, created = UserProductInteraction.objects.get_or_create(
            user=request.user,
            product=product
        )
        interaction.viewed = True
        interaction.view_count += 1
        interaction.save()
    
    # Get similar products
    similar_products = []
    if request.user.is_authenticated:
        model = RecommendationModel()
        model.train()
        similar_products = model.get_recommendations(request.user.id, top_n=4)
    
    context = {
        'product': product,
        'similar_products': similar_products
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def like_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        interaction, created = UserProductInteraction.objects.get_or_create(
            user=request.user,
            product=product
        )
        interaction.liked = True
        interaction.save()
        
        # Return JSON response
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

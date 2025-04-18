# products/management/commands/populate_sample_data.py
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product
from recommendations.models import UserProductInteraction


class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories = [
            {"name": "Electronics", "description": "Gadgets and devices"},
            {"name": "Clothing", "description": "Apparel and accessories"},
            {"name": "Books", "description": "Fiction and non-fiction books"},
            {"name": "Home & Kitchen", "description": "Items for your home"},
            {"name": "Sports & Outdoors", "description": "Sports equipment and outdoor gear"}
        ]
        
        created_categories = []
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]}
            )
            created_categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products
        products = [
            # Electronics
            {"name": "Smartphone X", "description": "Latest smartphone with cutting-edge features", "price": 999.99, "category": "Electronics", "stock": 50},
            {"name": "Laptop Pro", "description": "High-performance laptop for professionals", "price": 1299.99, "category": "Electronics", "stock": 30},
            {"name": "Wireless Earbuds", "description": "Premium sound quality with noise cancellation", "price": 149.99, "category": "Electronics", "stock": 100},
            {"name": "Smart Watch", "description": "Track your fitness and stay connected", "price": 249.99, "category": "Electronics", "stock": 75},
            {"name": "Digital Camera", "description": "Capture moments with crystal clarity", "price": 599.99, "category": "Electronics", "stock": 25},
            
            # Clothing
            {"name": "Casual T-Shirt", "description": "Comfortable cotton t-shirt for everyday wear", "price": 19.99, "category": "Clothing", "stock": 200},
            {"name": "Denim Jeans", "description": "Classic jeans for a timeless look", "price": 59.99, "category": "Clothing", "stock": 150},
            {"name": "Running Shoes", "description": "Lightweight shoes for optimal performance", "price": 89.99, "category": "Clothing", "stock": 100},
            {"name": "Winter Jacket", "description": "Stay warm during cold weather", "price": 129.99, "category": "Clothing", "stock": 80},
            {"name": "Formal Shirt", "description": "Elegant shirt for professional settings", "price": 49.99, "category": "Clothing", "stock": 120},
            
            # Books
            {"name": "Science Fiction Anthology", "description": "Collection of best sci-fi short stories", "price": 24.99, "category": "Books", "stock": 50},
            {"name": "History of Art", "description": "Comprehensive guide to art through the ages", "price": 39.99, "category": "Books", "stock": 30},
            {"name": "Cookbook: World Cuisines", "description": "Recipes from around the globe", "price": 29.99, "category": "Books", "stock": 60},
            {"name": "Programming in Python", "description": "Learn Python from basics to advanced", "price": 34.99, "category": "Books", "stock": 40},
            {"name": "Mystery Novel", "description": "Thrilling detective story with unexpected twists", "price": 14.99, "category": "Books", "stock": 70},
            
            # Home & Kitchen
            {"name": "Coffee Maker", "description": "Brew perfect coffee every morning", "price": 79.99, "category": "Home & Kitchen", "stock": 40},
            {"name": "Blender", "description": "Versatile blender for smoothies and more", "price": 69.99, "category": "Home & Kitchen", "stock": 35},
            {"name": "Bedding Set", "description": "Soft and comfortable bedding", "price": 99.99, "category": "Home & Kitchen", "stock": 50},
            {"name": "Kitchen Knife Set", "description": "Professional-grade kitchen knives", "price": 129.99, "category": "Home & Kitchen", "stock": 30},
            {"name": "Smart LED Bulbs", "description": "Energy-efficient lighting for your home", "price": 39.99, "category": "Home & Kitchen", "stock": 100},
            
            # Sports & Outdoors
            {"name": "Yoga Mat", "description": "Non-slip mat for yoga practice", "price": 29.99, "category": "Sports & Outdoors", "stock": 80},
            {"name": "Dumbbells Set", "description": "Adjustable weights for home workouts", "price": 149.99, "category": "Sports & Outdoors", "stock": 40},
            {"name": "Hiking Backpack", "description": "Durable backpack for outdoor adventures", "price": 79.99, "category": "Sports & Outdoors", "stock": 60},
            {"name": "Tennis Racket", "description": "Professional tennis racket for all levels", "price": 89.99, "category": "Sports & Outdoors", "stock": 35},
            {"name": "Camping Tent", "description": "Spacious tent for family camping trips", "price": 199.99, "category": "Sports & Outdoors", "stock": 25}
        ]
        
        created_products = []
        for product_data in products:
            category = next((c for c in created_categories if c.name == product_data["category"]), None)
            if category:
                product, created = Product.objects.get_or_create(
                    name=product_data["name"],
                    defaults={
                        "description": product_data["description"],
                        "price": product_data["price"],
                        "category": category,
                        "stock": product_data["stock"]
                    }
                )
                created_products.append(product)
                if created:
                    self.stdout.write(f'Created product: {product.name}')
        
        # Create users
        usernames = ['user1', 'user2', 'user3', 'user4', 'user5']
        created_users = []
        
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'password': 'password123'
                }
            )
            created_users.append(user)
            if created:
                self.stdout.write(f'Created user: {username}')
        
        # Create interactions
        for user in created_users:
            viewed_products = random.sample(created_products, min(15, len(created_products)))
            liked_products = random.sample(viewed_products, min(5, len(viewed_products)))
            purchased_products = random.sample(viewed_products, min(3, len(viewed_products)))
            
            for product in viewed_products:
                view_count = random.randint(1, 5)
                interaction, created = UserProductInteraction.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={
                        'viewed': True,
                        'view_count': view_count,
                        'liked': product in liked_products,
                        'purchased': product in purchased_products
                    }
                )
                if not created:
                    interaction.viewed = True
                    interaction.view_count = view_count
                    interaction.liked = product in liked_products
                    interaction.purchased = product in purchased_products
                    interaction.save()
                
                if created:
                    self.stdout.write(f'Created interaction: {user.username} - {product.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
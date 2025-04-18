from django.db import models
from django.contrib.auth.models import User
from products.models import Product
class UserProductInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    last_interaction = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'product')
from django.contrib import admin
from django.contrib.auth.models import User
from .models import *

admin.site.register(Product)  
admin.site.register(Category)
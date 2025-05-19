from django.contrib import admin
from .models import CustomUser, Author, Category, Book, Borrow
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Borrow)
from django.contrib import admin
from .models import Movie, Review

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    list_display = ['name', 'price', 'amount_left']
    list_editable = ['amount_left']
    fields = ['name', 'price', 'description', 'image', 'amount_left']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
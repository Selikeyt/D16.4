from django.contrib import admin
from .models import Category, Post

def nullfy_rating(modeladmin, request, queryset):
    queryset.update(post_rating=0.0)
nullfy_rating.short_description = 'Nullfy rating'

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'post_rating')
    list_filter = ('type', 'post_rating', 'author', 'category')
    search_fields = ('title', )
    actions = [nullfy_rating]


admin.site.register(Category)
admin.site.register(Post, PostAdmin)


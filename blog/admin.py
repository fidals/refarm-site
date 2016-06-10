from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'type', 'position', 'title', 'h1',
              'keywords', 'description', 'content')

admin.site.register(Post)

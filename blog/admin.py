from django.contrib import admin

from .models import Post



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_pub')
    list_filter = ('date_pub',)

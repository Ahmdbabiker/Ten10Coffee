from django.contrib import admin
from .models import * 


admin.site.register(Profile)
admin.site.register(Tag)

@admin.register(Product)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':['name']}

admin.site.register(Rating)

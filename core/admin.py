from django.contrib import admin
from .models import *



admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(City)

@admin.register(Product)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':['name']}

admin.site.register(Rating)
admin.site.register(Extra)



@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

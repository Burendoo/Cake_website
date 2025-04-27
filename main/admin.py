from django.contrib import admin
from .models import CakeModel, Flavour


# Register your models here.


class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'short_description')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    actions = ['delete_selected']

    def save_model(self, request, obj, form, change):
        if not obj.slug:  # If slug is empty
            obj.slug = obj._generate_unique_slug()
        super().save_model(request, obj, form, change)

class FlavourAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('flavour_name',)}


admin.site.register(CakeModel, CakeAdmin)
admin.site.register(Flavour, FlavourAdmin) 


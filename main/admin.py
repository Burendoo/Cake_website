from django.contrib import admin
from .models import CakeModel, Flavour


# Register your models here.


class CakeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'price', 'short_description')
    list_display_links = ('name',)
    search_fields = ('name', 'description')
    actions = ['delete_selected']

class FlavourAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('flavour_name',)}


admin.site.register(CakeModel, CakeAdmin)
admin.site.register(Flavour, FlavourAdmin) 


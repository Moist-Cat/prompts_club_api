from django.contrib import admin
from .models import Folder

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_dilplay = ('name', 'description')
    search_fields = ('name','description')
    prepopulated_fields = {'slug' : ('name',)}
    ordering = ('name',)

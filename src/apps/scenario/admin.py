from django.contrib import admin
from .models import Scenario, WorldInfo, \
                    Rating

class WIInline(admin.TabularInline):
    model = WorldInfo
    raw_id_fields = ['scenario']

class RatingInline(admin.TabularInline):
    model = Rating
    raw_id_fields = ['scenario']

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):    
    list_display = ('title','slug','user','publish','status', 'tags')
    list_filter = ('status','created','publish','user') 
    search_fields = ('title','body') # search bar
    prepopulated_fields = {'slug' : ('title',)}
    raw_id_fields = ('user',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    
    inlines = [WIInline, RatingInline]

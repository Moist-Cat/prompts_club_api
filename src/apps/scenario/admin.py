from django.contrib import admin
from .models import Scenario, Comment, \
                    Rating, WorldInfo

class WIInline(admin.TabularInline):
    model = WorldInfo
    raw_id_fields = ['scenario']

class RatingInline(admin.TabularInline):
    model = Rating
    raw_id_fields = ['scenario']

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):    
    list_display = ('title','slug','author','publish','status', 'tags')
    list_filter = ('status','created','publish','author') 
    search_fields = ('title','body') # search bar
    prepopulated_fields = {'slug' : ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    
    inlines = [WIInline, RatingInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_dilplay = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')

from django.contrib import admin

from .models import Category, Genre, GenreTitle, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'description', 'category')
    search_fields = ('name',)
    list_filter = ('year',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """_summary_

    Args:
        admin (_type_): _description_
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """_summary_

    Args:
        admin (_type_): _description_
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    """_summary_

    Args:
        admin (_type_): _description_
    """
    list_display = ('genre', 'title')

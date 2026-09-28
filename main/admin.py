from django.contrib import admin

from .models import Achievement, Experience


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "issuer", "year")
    search_fields = ("name", "issuer")
    filter_horizontal = ("starred_by",)


admin.site.register(Experience)

from django.urls import path

from main.views import show_main, show_experience, show_achievements, create_achievement, get_achievements_json, delete_achievement

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("achievements/", show_achievements, name="show_achievements"),
    path("achievements/add/", create_achievement, name="create_achievement"),
    path("api/achievements/", get_achievements_json, name="get_achievements_json"),
    path("achievements/<uuid:achievement_id>/delete/", delete_achievement, name="delete_achievement"),
]

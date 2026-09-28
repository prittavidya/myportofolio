from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_achievements,
    create_achievement,
    edit_achievement,
    get_achievements_json,
    get_experience_json,
    delete_achievement,
    register,
    login_user,
    logout_user,
    toggle_star,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("achievements/", show_achievements, name="show_achievements"),
    path("achievements/add/", create_achievement, name="create_achievement"),
    path("achievements/<uuid:achievement_id>/edit/", edit_achievement, name="edit_achievement"),
    path("api/achievements/", get_achievements_json, name="get_achievements_json"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("achievements/<uuid:achievement_id>/delete/", delete_achievement, name="delete_achievement"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("achievements/<uuid:achievement_id>/star/", toggle_star, name="toggle_star"),
]

from django.shortcuts import render

from main.models import Experience
from main.models import Achievement

from django.contrib import messages
from django.shortcuts import render, redirect
from main.forms import AchievementForm

from django.core import serializers
from django.http import HttpResponse

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.shortcuts import get_object_or_404
import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Joanna Prittavidya Putri Arianto",
        "npm": "2506539265",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Motivated second-year Information System student with a strong "
            "foundation in Mathematics."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Joanna Prittavidya Putri Arianto",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_achievements(request):
    json_response = get_achievements_json(request)

    achievements = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    achievements = [achievement.object for achievement in achievements]
    
    name_query = request.GET.get("name", "").strip() 

    context = {
        "name": "Joanna", 
        "achievements": achievements,
        "name_query": name_query,
    }
    return render(request, "achievements.html", context)

@login_required(login_url="/login/")
def create_achievement(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = AchievementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Achievement baru berhasil ditambahkan!")
        return redirect("main:show_achievements")

    context = {
        "name": "Joanna", 
        "form": form,
        "is_edit": False,
    }
    return render(request, "achievement_form.html", context)

@login_required(login_url="/login/")
def edit_achievement(request, achievement_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    achievement = get_object_or_404(Achievement, pk=achievement_id)
    # instance= membuat form terisi data lama dan menyimpan sebagai UPDATE, bukan INSERT
    form = AchievementForm(request.POST or None, instance=achievement)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Achievement berhasil diperbarui!")
        return redirect("main:show_achievements")

    context = {
        "name": "Joanna",
        "form": form,
        "is_edit": True,
        "achievement": achievement,
    }
    return render(request, "achievement_form.html", context)

def get_achievements_json(request):
    name_query = request.GET.get("name", "").strip() 
    achievements = Achievement.objects.all()

    if name_query:
        achievements = achievements.filter(name__icontains=name_query)

    achievements_json = serializers.serialize(
        "json", achievements, use_natural_foreign_keys=True
    )
    
    return HttpResponse(achievements_json, content_type="application/json")

def get_experience_json(request):
    experience_json = serializers.serialize("json", Experience.objects.all())
    return HttpResponse(experience_json, content_type="application/json")

@login_required(login_url="/login/")
def delete_achievement(request, achievement_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    # Mengambil objek berdasarkan ID, atau memunculkan error 404 jika tidak ada
    achievement = get_object_or_404(Achievement, pk=achievement_id)

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Achievement berhasil dihapus!")
        return redirect("main:show_achievements")

    return redirect("main:show_achievements")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Joanna",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Joanna",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_star(request, achievement_id):
    achievement = get_object_or_404(Achievement, pk=achievement_id)

    if request.method == "POST":
        if request.user in achievement.starred_by.all():
            achievement.starred_by.remove(request.user)
        else:
            achievement.starred_by.add(request.user)

    return redirect("main:show_achievements")

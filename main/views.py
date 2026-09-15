from django.shortcuts import render

from main.models import Experience
from main.models import Achievement

from django.contrib import messages
from django.shortcuts import render, redirect
from main.forms import AchievementForm

from django.core import serializers
from django.http import HttpResponse

from django.shortcuts import get_object_or_404

def show_main(request):
    context = {
        "name": "Joanna Prittavidya Putri Arianto",
        "npm": "2506539265",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Motivated second-year Information System student with a strong "
            "foundation in Mathematics."
        ),
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

def create_achievement(request):
    form = AchievementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Achievement baru berhasil ditambahkan!")
        return redirect("main:show_achievements")

    context = {
        "name": "Joanna", 
        "form": form,
    }
    return render(request, "achievement_form.html", context)

def get_achievements_json(request):
    name_query = request.GET.get("name", "").strip() 
    achievements = Achievement.objects.all()

    if name_query:
        achievements = achievements.filter(name__icontains=name_query)

    achievements_json = serializers.serialize("json", achievements)
    
    return HttpResponse(achievements_json, content_type="application/json")

def delete_achievement(request, achievement_id):
    # Mengambil objek berdasarkan ID, atau memunculkan error 404 jika tidak ada
    achievement = get_object_or_404(Achievement, pk=achievement_id)

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Achievement berhasil dihapus!")
        return redirect("main:show_achievements")

    return redirect("main:show_achievements")
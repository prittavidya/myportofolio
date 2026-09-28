import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from main.forms import AchievementForm
from main.models import Achievement, Experience
from main.roles import (
    can_create_or_delete_achievement,
    can_edit_achievement,
    role_required,
)

# Field yang aman dipublikasikan lewat API. `starred_by` sengaja tidak disertakan
# agar daftar akun pengguna tidak bocor ke publik.
ACHIEVEMENT_PUBLIC_FIELDS = ("name", "issuer", "year", "description")


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


def filter_achievements(request):
    """QuerySet achievement dengan filter opsional `?name=` (dipakai halaman dan API)."""
    name_query = request.GET.get("name", "").strip()
    achievements = Achievement.objects.all()
    if name_query:
        achievements = achievements.filter(name__icontains=name_query)
    return achievements, name_query


def get_starred_ids(user):
    """ID achievement yang sudah diberi star oleh `user` (kosong bagi pengunjung)."""
    if not user.is_authenticated:
        return set()
    return set(user.starred_achievements.values_list("id", flat=True))


def show_achievements(request):
    achievements, name_query = filter_achievements(request)
    context = {
        "name": "Joanna",
        # Jumlah star dihitung sekali lewat satu query, bukan per kartu di template
        "achievements": achievements.annotate(star_count=Count("starred_by")),
        "starred_ids": get_starred_ids(request.user),
        "name_query": name_query,
    }
    return render(request, "achievements.html", context)


def show_achievement_detail(request, achievement_id):
    achievement = get_object_or_404(
        Achievement.objects.annotate(star_count=Count("starred_by")), pk=achievement_id
    )
    context = {
        "name": "Joanna",
        "achievement": achievement,
        "starred_ids": get_starred_ids(request.user),
    }
    return render(request, "achievement_detail.html", context)


@role_required(can_create_or_delete_achievement)
def create_achievement(request):
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


@role_required(can_edit_achievement)
def edit_achievement(request, achievement_id):
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


@role_required(can_create_or_delete_achievement)
def delete_achievement(request, achievement_id):
    # Mengambil objek berdasarkan ID, atau memunculkan error 404 jika tidak ada
    achievement = get_object_or_404(Achievement, pk=achievement_id)

    if request.method == "POST":
        achievement.delete()
        messages.success(request, "Achievement berhasil dihapus!")

    return redirect("main:show_achievements")


def get_achievements_json(request):
    achievements, _ = filter_achievements(request)
    achievements_json = serializers.serialize(
        "json", achievements, fields=ACHIEVEMENT_PUBLIC_FIELDS
    )
    return HttpResponse(achievements_json, content_type="application/json")


def get_experience_json(request):
    experience_json = serializers.serialize("json", Experience.objects.all())
    return HttpResponse(experience_json, content_type="application/json")


def safe_next_url(request, fallback):
    """Ambil `next` dari request hanya jika mengarah ke situs ini (cegah open redirect)."""
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return fallback


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
        login(request, form.get_user())
        # Kembali ke halaman yang tadinya meminta login (?next=), jika ada
        response = redirect(safe_next_url(request, "main:show_main"))
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Joanna",
        "form": form,
        "next": request.GET.get("next", ""),
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response


@login_required
@require_POST
def toggle_star(request, achievement_id):
    """Memberi atau membatalkan star; M2M menjamin maksimal satu star per pengguna."""
    achievement = get_object_or_404(Achievement, pk=achievement_id)

    if achievement.starred_by.filter(pk=request.user.pk).exists():
        achievement.starred_by.remove(request.user)
    else:
        achievement.starred_by.add(request.user)

    return redirect(safe_next_url(request, "main:show_achievements"))

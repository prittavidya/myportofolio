from django.shortcuts import render

from main.models import Experience


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

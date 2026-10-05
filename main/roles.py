"""Aturan hak akses bagian Achievements.

| Peran            | Baca | Star | Ubah | Buat / Hapus |
|------------------|------|------|------|--------------|
| Pengunjung       |  ya  |  -   |  -   |      -       |
| Pengguna biasa   |  ya  |  ya  |  -   |      -       |
| Editor           |  ya  |  ya  |  ya  |      -       |
| Pemilik (super)  |  ya  |  ya  |  ya  |      ya      |

Editor adalah anggota grup Django bernama "Editor" (dibuat oleh migrasi 0007,
anggotanya ditetapkan lewat Django Admin).
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

EDITOR_GROUP = "Editor"


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP).exists()


def can_edit_achievement(user):
    return user.is_superuser or is_editor(user)


def can_create_or_delete_achievement(user):
    return user.is_superuser


def get_role_label(user):
    if not user.is_authenticated:
        return ""
    if user.is_superuser:
        return "Pemilik"
    if is_editor(user):
        return "Editor"
    return "Pengguna"


def wants_json(request):
    """True jika permintaan berasal dari fetch() yang meminta balasan JSON."""
    return "application/json" in request.headers.get("Accept", "")


def json_login_required(view):
    """Seperti `login_required`, tetapi permintaan AJAX mendapat JSON 401.

    Redirect ke halaman login tidak berguna bagi fetch(): browser akan mengikuti
    redirect dan menerima HTML halaman login, bukan JSON yang bisa dibaca.
    """

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view(request, *args, **kwargs)
        if wants_json(request):
            return JsonResponse({"message": "Sesi berakhir, silakan login kembali."}, status=401)
        return redirect_to_login(request.get_full_path())

    return wrapper


def role_required(check):
    """Wajib login, lalu 403 jika `check(user)` gagal (JSON untuk permintaan AJAX)."""

    def decorator(view):
        @wraps(view)
        @json_login_required
        def wrapper(request, *args, **kwargs):
            if not check(request.user):
                if wants_json(request):
                    return JsonResponse({"message": "Kamu tidak berhak melakukan aksi ini."}, status=403)
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator

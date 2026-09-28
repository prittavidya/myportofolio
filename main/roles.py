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

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

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


def role_required(check):
    """Wajib login (redirect ke halaman login), lalu 403 jika `check(user)` gagal."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not check(request.user):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator

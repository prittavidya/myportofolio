from rest_framework.permissions import BasePermission, SAFE_METHODS

from main.roles import can_create_or_delete_achievement, can_edit_achievement


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Menerapkan tabel peran di main/roles.py pada API Achievements.

    Baca: semua pengunjung. PUT/PATCH: Editor dan pemilik. POST/DELETE: hanya pemilik.
    """

    message = "Kamu tidak berhak melakukan aksi ini."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.method in ("PUT", "PATCH"):
            return can_edit_achievement(request.user)
        return can_create_or_delete_achievement(request.user)

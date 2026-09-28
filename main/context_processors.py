from main.roles import (
    can_create_or_delete_achievement,
    can_edit_achievement,
    get_role_label,
    is_editor,
)


def user_roles(request):
    """Menyediakan flag peran ke semua template agar tombol aksi bisa disembunyikan."""
    user = request.user
    return {
        "is_editor": is_editor(user),
        "can_edit_achievement": can_edit_achievement(user),
        "can_manage_achievement": can_create_or_delete_achievement(user),
        "user_role": get_role_label(user),
    }

from django.contrib.auth.management import create_permissions
from django.db import migrations

EDITOR_GROUP = "Editor"
EDITOR_PERMISSIONS = ["view_achievement", "change_achievement"]


def create_editor_group(apps, schema_editor):
    """Membuat grup Editor yang hanya boleh melihat dan mengubah Achievement.

    Permission bawaan Django biasanya baru dibuat setelah seluruh migrasi selesai
    (sinyal post_migrate), jadi dibuat lebih dulu di sini agar dapat dipasang ke grup.
    """
    app_config = apps.get_app_config("main")
    app_config.models_module = True
    create_permissions(app_config, apps=apps, verbosity=0)
    app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    group, _ = Group.objects.get_or_create(name=EDITOR_GROUP)
    group.permissions.add(
        *Permission.objects.filter(
            content_type__app_label="main", codename__in=EDITOR_PERMISSIONS
        )
    )


def delete_editor_group(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name=EDITOR_GROUP).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_achievement_starred_cleanup"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(create_editor_group, delete_editor_group),
    ]

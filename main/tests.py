import json
import uuid

from django.contrib.auth.models import Group, User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from main.models import Experience
from .models import Achievement


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

class AchievementTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_url_exists_at_correct_location_and_uses_template(self):
        """Test apakah URL achievements bisa diakses dan memakai template yang benar"""
        response = self.client.get(reverse('main:show_achievements'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'achievements.html')

    def test_empty_state_message_is_shown(self):
        """Test apakah pesan kondisi kosong muncul ketika belum ada data achievement"""
        response = self.client.get(reverse('main:show_achievements'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada achievement yang ditambahkan.")

    def test_achievement_data_is_loaded_via_ajax(self):
        """Halaman hanya memuat kerangka; data achievement diambil dari endpoint JSON"""
        Achievement.objects.create(
            name="Juara 1 Hackathon",
            issuer="Fasilkom UI",
            year=2026
        )
        response = self.client.get(reverse('main:show_achievements'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Juara 1 Hackathon")
        self.assertContains(response, reverse('main:get_achievements_json'))

        data = json.loads(self.client.get(reverse('main:get_achievements_json')).content)
        self.assertEqual(data[0]["fields"]["name"], "Juara 1 Hackathon")
        self.assertEqual(data[0]["fields"]["issuer"], "Fasilkom UI")
        self.assertEqual(data[0]["fields"]["year"], 2026)

    def test_search_query_is_prefilled(self):
        response = self.client.get(reverse('main:show_achievements'), {"name": "hackathon"})
        self.assertContains(response, 'value="hackathon"')


class AchievementFormAndApiTest(TestCase):
    def setUp(self):
        self.achievement = Achievement.objects.create(
            name="Juara 1 Hackathon",
            issuer="Fasilkom UI",
            year=2026,
            description="Kompetisi tingkat fakultas.",
        )
        self.valid_data = {
            "name": "Dean's List",
            "issuer": "Universitas Indonesia",
            "year": 2025,
            "description": "",
        }
        self.owner = User.objects.create_superuser("owner", password="owner-pass-123")
        self.client.force_login(self.owner)

    def test_create_form_page_renders(self):
        response = self.client.get(reverse("main:create_achievement"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "achievement_form.html")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_create_achievement_saves_and_redirects(self):
        response = self.client.post(reverse("main:create_achievement"), self.valid_data)

        self.assertRedirects(response, reverse("main:show_achievements"))
        self.assertTrue(Achievement.objects.filter(name="Dean's List").exists())

    def test_create_achievement_invalid_data_is_rejected(self):
        data = {**self.valid_data, "year": "bukan-angka"}
        response = self.client.post(reverse("main:create_achievement"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Achievement.objects.count(), 1)
        self.assertContains(response, "form-error")

    def test_edit_form_is_prefilled(self):
        url = reverse("main:edit_achievement", args=[self.achievement.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Juara 1 Hackathon")
        self.assertContains(response, "Simpan Perubahan")

    def test_edit_achievement_updates_same_record(self):
        url = reverse("main:edit_achievement", args=[self.achievement.id])
        response = self.client.post(url, {**self.valid_data, "name": "Juara 2 Hackathon"})

        self.assertRedirects(response, reverse("main:show_achievements"))
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.name, "Juara 2 Hackathon")
        self.assertEqual(Achievement.objects.count(), 1)

    def test_edit_unknown_achievement_returns_404(self):
        url = reverse("main:edit_achievement", args=[uuid.uuid4()])

        self.assertEqual(self.client.get(url).status_code, 404)

    def test_delete_achievement_via_post(self):
        url = reverse("main:delete_achievement", args=[self.achievement.id])
        response = self.client.post(url)

        self.assertRedirects(response, reverse("main:show_achievements"))
        self.assertFalse(Achievement.objects.exists())

    def test_delete_achievement_via_get_does_not_delete(self):
        url = reverse("main:delete_achievement", args=[self.achievement.id])
        self.client.get(url)

        self.assertTrue(Achievement.objects.exists())

    def test_achievements_json(self):
        response = self.client.get(reverse("main:get_achievements_json"))
        data = json.loads(response.content)

        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["model"], "main.achievement")
        self.assertEqual(data[0]["pk"], str(self.achievement.id))
        self.assertEqual(data[0]["fields"]["name"], "Juara 1 Hackathon")

    def test_achievements_json_name_filter(self):
        url = reverse("main:get_achievements_json")

        self.assertEqual(len(json.loads(self.client.get(url, {"name": "hackathon"}).content)), 1)
        self.assertEqual(len(json.loads(self.client.get(url, {"name": "zzz"}).content)), 0)

    def test_experience_json(self):
        Experience.objects.create(title="Asisten Dosen", description="Membantu mahasiswa.")
        response = self.client.get(reverse("main:get_experience_json"))
        data = json.loads(response.content)

        self.assertEqual(data[0]["fields"]["title"], "Asisten Dosen")

    def test_pages_extend_base_template(self):
        for name in ("show_main", "show_experience", "show_achievements", "create_achievement"):
            with self.subTest(page=name):
                response = self.client.get(reverse(f"main:{name}"))
                self.assertTemplateUsed(response, "base.html")

    def test_flash_message_is_shown_after_create(self):
        response = self.client.post(
            reverse("main:create_achievement"), self.valid_data, follow=True
        )

        self.assertContains(response, "Achievement baru berhasil ditambahkan!")


class AuthAndAuthorizationTest(TestCase):
    def setUp(self):
        self.achievement = Achievement.objects.create(
            name="Juara 1 Hackathon", issuer="Fasilkom UI", year=2026
        )
        self.password = "sasha-pass-123"
        self.user = User.objects.create_user("sasha", password=self.password)
        self.owner = User.objects.create_superuser("owner", password="owner-pass-123")

    def test_register_creates_account_and_redirects_to_login(self):
        response = self.client.post(reverse("main:register"), {
            "username": "rian",
            "password1": "Rahasia-Kuat-123",
            "password2": "Rahasia-Kuat-123",
        })

        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="rian").exists())

    def test_register_mismatched_password_is_rejected(self):
        response = self.client.post(reverse("main:register"), {
            "username": "rian",
            "password1": "Rahasia-Kuat-123",
            "password2": "Beda-Password-123",
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="rian").exists())

    def test_login_sets_last_login_cookie_and_logout_clears_it(self):
        response = self.client.post(reverse("main:login"), {
            "username": "sasha", "password": self.password,
        })

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)
        self.assertContains(self.client.get(reverse("main:show_main")), "sasha")

        response = self.client.get(reverse("main:logout"))
        self.assertEqual(response.cookies["last_login"].value, "")
        self.assertContains(self.client.get(reverse("main:show_main")), "Login")

    def test_login_wrong_password_shows_error(self):
        response = self.client.post(reverse("main:login"), {
            "username": "sasha", "password": "salah",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")

    def test_anonymous_is_redirected_to_login(self):
        for name, args in (
            ("create_achievement", []),
            ("edit_achievement", [self.achievement.id]),
            ("delete_achievement", [self.achievement.id]),
            ("toggle_star", [self.achievement.id]),
        ):
            with self.subTest(view=name):
                response = self.client.post(reverse(f"main:{name}", args=args))
                self.assertTrue(response.url.startswith("/login/?next="))

    def test_regular_user_is_forbidden_from_changing_achievements(self):
        self.client.force_login(self.user)
        for name, args in (
            ("create_achievement", []),
            ("edit_achievement", [self.achievement.id]),
            ("delete_achievement", [self.achievement.id]),
        ):
            with self.subTest(view=name):
                response = self.client.post(reverse(f"main:{name}", args=args))
                self.assertEqual(response.status_code, 403)
        self.assertTrue(Achievement.objects.exists())

    def test_owner_controls_hidden_from_regular_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("main:show_achievements"))

        # Kartu dirakit JavaScript, jadi yang diuji adalah flag peran dan modal di halaman
        self.assertNotContains(response, "Tambah Achievement")
        self.assertNotContains(response, 'id="add-achievement-modal"')
        self.assertNotContains(response, 'id="delete-achievement-modal"')
        self.assertContains(response, 'IS_AUTHENTICATED = "true"')
        self.assertContains(response, 'CAN_MANAGE = "false"')

    def test_owner_sees_controls(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("main:show_achievements"))

        self.assertContains(response, "Tambah Achievement")
        self.assertContains(response, 'id="add-achievement-modal"')
        self.assertContains(response, 'id="delete-achievement-modal"')
        self.assertContains(response, 'CAN_MANAGE = "true"')

    def test_toggle_star_adds_and_removes(self):
        self.client.force_login(self.user)
        url = reverse("main:toggle_star", args=[self.achievement.id])

        self.client.post(url)
        self.assertIn(self.user, self.achievement.starred_by.all())
        self.client.post(url)
        self.assertNotIn(self.user, self.achievement.starred_by.all())

    def test_star_via_get_does_not_change_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("main:toggle_star", args=[self.achievement.id]))

        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.achievement.starred_by.exists())

    def test_star_is_limited_to_one_per_user(self):
        other = User.objects.create_user("budi", password="budi-pass-123")
        url = reverse("main:toggle_star", args=[self.achievement.id])
        self.client.force_login(self.user)
        self.client.post(url)
        self.client.force_login(other)
        self.client.post(url)

        self.assertEqual(self.achievement.starred_by.count(), 2)
        response = self.client.get(reverse("main:get_achievements_json"))
        fields = json.loads(response.content)[0]["fields"]
        self.assertEqual(fields["star_count"], 2)
        self.assertTrue(fields["is_starred"])

    def test_star_redirects_back_to_safe_next_only(self):
        self.client.force_login(self.user)
        url = reverse("main:toggle_star", args=[self.achievement.id])
        detail = reverse("main:show_achievement_detail", args=[self.achievement.id])

        self.assertRedirects(self.client.post(url, {"next": detail}), detail)
        response = self.client.post(url, {"next": "https://evil.example.com/"})
        self.assertRedirects(response, reverse("main:show_achievements"))

    def test_anonymous_sees_login_prompt_instead_of_star_form(self):
        response = self.client.get(reverse("main:show_achievements"))

        self.assertContains(response, 'IS_AUTHENTICATED = "false"')
        self.assertContains(response, 'CAN_EDIT = "false"')
        self.assertNotContains(response, "Tambah Achievement")

        self.achievement.starred_by.add(self.user)
        fields = json.loads(self.client.get(reverse("main:get_achievements_json")).content)[0]["fields"]
        self.assertFalse(fields["is_starred"])
        self.assertEqual(fields["star_count"], 1)

    def test_login_redirects_to_next(self):
        response = self.client.post(
            reverse("main:login") + "?next=/achievements/",
            {"username": "sasha", "password": self.password, "next": "/achievements/"},
        )

        self.assertRedirects(response, reverse("main:show_achievements"))

    def test_json_does_not_leak_starring_users(self):
        self.achievement.starred_by.add(self.user)
        response = self.client.get(reverse("main:get_achievements_json"))
        fields = json.loads(response.content)[0]["fields"]

        self.assertNotIn("starred_by", fields)
        self.assertNotContains(response, "sasha")
        self.assertEqual(
            set(fields),
            {"name", "issuer", "year", "description", "star_count", "is_starred"},
        )

    def test_detail_page_is_public(self):
        url = reverse("main:show_achievement_detail", args=[self.achievement.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "achievement_detail.html")
        self.assertContains(response, "Juara 1 Hackathon")
        self.assertEqual(
            self.client.get(reverse("main:show_achievement_detail", args=[uuid.uuid4()])).status_code,
            404,
        )


class EditorRoleTest(TestCase):
    def setUp(self):
        self.achievement = Achievement.objects.create(
            name="Juara 1 Hackathon", issuer="Fasilkom UI", year=2026
        )
        self.editor = User.objects.create_user("edi", password="edi-pass-123")
        # Grup Editor dibuat oleh migrasi 0007_create_editor_group
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.client.force_login(self.editor)

    def test_editor_group_has_change_permission_only(self):
        codenames = set(
            Group.objects.get(name="Editor").permissions.values_list("codename", flat=True)
        )

        self.assertEqual(codenames, {"view_achievement", "change_achievement"})

    def test_editor_can_edit(self):
        url = reverse("main:edit_achievement", args=[self.achievement.id])
        response = self.client.post(url, {
            "name": "Juara 2 Hackathon", "issuer": "Fasilkom UI", "year": 2026, "description": "",
        })

        self.assertRedirects(response, reverse("main:show_achievements"))
        self.achievement.refresh_from_db()
        self.assertEqual(self.achievement.name, "Juara 2 Hackathon")

    def test_editor_cannot_create_or_delete(self):
        self.assertEqual(self.client.get(reverse("main:create_achievement")).status_code, 403)
        response = self.client.post(reverse("main:delete_achievement", args=[self.achievement.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Achievement.objects.exists())

    def test_editor_can_star(self):
        self.client.post(reverse("main:toggle_star", args=[self.achievement.id]))

        self.assertIn(self.editor, self.achievement.starred_by.all())

    def test_editor_sees_only_edit_control(self):
        response = self.client.get(reverse("main:show_achievements"))

        self.assertContains(response, 'CAN_EDIT = "true"')
        self.assertContains(response, 'CAN_MANAGE = "false"')
        self.assertNotContains(response, "Tambah Achievement")
        self.assertNotContains(response, 'id="delete-achievement-modal"')
        self.assertContains(response, "role-badge\">Editor")

    def test_editor_cannot_create_via_ajax(self):
        response = self.client.post(reverse("main:create_achievement_ajax"), {
            "name": "Lomba", "issuer": "UI", "year": 2026, "description": "",
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Achievement.objects.count(), 1)


class AjaxAndToastTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("owner", password="owner-pass-123")
        self.user = User.objects.create_user("sasha", password="sasha-pass-123")
        self.url = reverse("main:create_achievement_ajax")
        self.valid_data = {
            "name": "Dean's List", "issuer": "Universitas Indonesia", "year": 2025, "description": "",
        }

    def test_toast_component_is_on_every_page(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, 'id="toast-component"')
        self.assertContains(response, "js/toast.js")

    def test_owner_creates_achievement_via_ajax(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, self.valid_data)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 201)
        achievement = Achievement.objects.get(name="Dean's List")
        self.assertEqual(data["pk"], str(achievement.id))
        self.assertIn("berhasil", data["message"])

    def test_ajax_invalid_data_returns_field_errors(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, {**self.valid_data, "year": "bukan-angka"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("year", json.loads(response.content)["errors"])
        self.assertFalse(Achievement.objects.exists())

    def test_ajax_rejects_anonymous_and_regular_user_with_json(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["Content-Type"], "application/json")

        self.client.force_login(self.user)
        self.assertEqual(self.client.post(self.url, self.valid_data).status_code, 403)
        self.assertFalse(Achievement.objects.exists())

    def test_ajax_create_requires_post(self):
        self.client.force_login(self.owner)

        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_ajax_create_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)

        self.assertEqual(client.post(self.url, self.valid_data).status_code, 403)
        self.assertFalse(Achievement.objects.exists())

    def test_html_tags_are_stripped_on_server(self):
        self.client.force_login(self.owner)
        self.client.post(self.url, {
            **self.valid_data,
            "name": "<script>alert('xss')</script>Lomba",
            "description": "<img src=x onerror=alert(1)>Deskripsi",
        })
        achievement = Achievement.objects.get()

        self.assertEqual(achievement.name, "alert('xss')Lomba")
        self.assertEqual(achievement.description, "Deskripsi")

    def test_name_with_only_tags_is_rejected(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, {**self.valid_data, "name": "<b></b>"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", json.loads(response.content)["errors"])

    def test_page_escapes_output_in_javascript(self):
        response = self.client.get(reverse("main:show_achievements"))

        self.assertContains(response, "function escapeHtml")

    def test_flash_messages_are_passed_to_toast(self):
        self.client.force_login(self.owner)
        achievement = Achievement.objects.create(name="Lomba", issuer="UI", year=2026)
        response = self.client.post(
            reverse("main:delete_achievement", args=[achievement.id]), follow=True
        )

        self.assertContains(response, 'id="django-messages"')
        self.assertContains(response, "Achievement berhasil dihapus!")

    def test_flash_message_is_escaped_in_json(self):
        from django.contrib.messages import constants
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.template.loader import render_to_string
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        request.user = self.owner
        request.session = self.client.session
        storage = FallbackStorage(request)
        request._messages = storage
        storage.add(constants.SUCCESS, '</script><script>alert(1)</script>')
        html = render_to_string("base.html", request=request)

        self.assertNotIn("<script>alert(1)</script>", html)

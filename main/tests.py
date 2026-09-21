import json
import uuid

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

    def test_achievement_data_is_rendered(self):
        """Test apakah data achievement muncul di halaman HTML ketika ada data"""
        Achievement.objects.create(
            name="Juara 1 Hackathon",
            issuer="Fasilkom UI",
            year=2026
        )
        response = self.client.get(reverse('main:show_achievements'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Juara 1 Hackathon")
        self.assertContains(response, "Fasilkom UI")
        self.assertContains(response, "2026")
        self.assertNotContains(response, "Belum ada achievement yang ditambahkan.")


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


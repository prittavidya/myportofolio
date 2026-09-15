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


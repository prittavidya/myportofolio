from django.forms import ModelForm, NumberInput, Textarea, TextInput

from main.models import Achievement


class AchievementForm(ModelForm):
    """Form untuk membuat dan mengubah Achievement.

    `id` tidak dimasukkan karena dibuat otomatis (UUID) dan tidak boleh diubah.
    """

    class Meta:
        model = Achievement
        fields = ["name", "issuer", "year", "description"]

        labels = {
            "name": "Nama Pencapaian",
            "issuer": "Penyelenggara / Institusi",
            "year": "Tahun",
            "description": "Deskripsi (opsional)",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Contoh: Juara 1 Lomba Programming",
                    "maxlength": 255,
                }
            ),
            "issuer": TextInput(
                attrs={
                    "placeholder": "Contoh: Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "year": NumberInput(
                attrs={
                    "placeholder": "Contoh: 2026",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan singkat tentang pencapaian ini",
                    "rows": 4,
                }
            ),
        }

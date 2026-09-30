from django.core.exceptions import ValidationError
from django.forms import ModelForm, NumberInput, Textarea, TextInput
from django.utils.html import strip_tags

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

    # Membersihkan tag HTML di server agar input seperti <script> tidak tersimpan.
    # Escaping di JavaScript tetap diperlukan sebagai lapisan pertahanan kedua.
    def _clean_required_text(self, field):
        value = strip_tags(self.cleaned_data[field]).strip()
        if not value:
            raise ValidationError("Field ini tidak boleh hanya berisi tag HTML.")
        return value

    def clean_name(self):
        return self._clean_required_text("name")

    def clean_issuer(self):
        return self._clean_required_text("issuer")

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

from django.forms import ModelForm, TextInput, NumberInput
from main.models import Achievement

class AchievementForm(ModelForm):
    class Meta:
        model = Achievement
        fields = [
            "name", 
            "issuer", 
            "year"
        ]

        labels = {
            "name": "Nama Pencapaian",
            "issuer": "Penyelenggara / Institusi",
            "year": "Tahun",
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
        }
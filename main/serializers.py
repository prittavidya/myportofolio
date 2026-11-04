from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Achievement


class AchievementSerializer(serializers.ModelSerializer):
    # `starred_by` sengaja tidak diekspos: API hanya memberi jumlah star dan status
    # star milik pengguna yang sedang login, agar daftar akun tidak bocor ke publik.
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ["id", "name", "issuer", "year", "description", "star_count", "is_starred"]
        read_only_fields = ["id"]

    # Serializer tidak menjalankan AchievementForm, jadi aturan pembersihan yang
    # sama perlu ada di sini. Escaping di JavaScript tetap diperlukan saat menampilkan.
    def _clean_required_text(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Field ini tidak boleh hanya berisi tag HTML.")
        return value

    def validate_name(self, value):
        return self._clean_required_text(value)

    def validate_issuer(self, value):
        return self._clean_required_text(value)

    def validate_description(self, value):
        return strip_tags(value).strip()

    def get_star_count(self, obj):
        # len(.all()) memakai hasil prefetch_related; .count() selalu query ulang per objek
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

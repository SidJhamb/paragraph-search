from rest_framework import serializers

from core.models import (
    Paragraph
)


class ParagraphSerializer(serializers.ModelSerializer):
    """Serializer for Paragraphs."""

    class Meta:
        model = Paragraph
        fields = ['id', 'text']
        read_only_fields = ['id']
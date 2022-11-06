"""
Tests for models.
"""
from core import models
from django.test import TestCase


class ModelTests(TestCase):
    """Test models."""

    def test_create_paragraph(self):
        """Test creating a paragraph is successful."""
        paragraph = models.Paragraph.objects.create(text='text')
        self.assertEqual(paragraph.text, 'text')

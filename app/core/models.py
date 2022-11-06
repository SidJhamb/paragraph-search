"""
Database models.
"""
from django.db import models


class Paragraph(models.Model):
    """Paragraphs in the system."""
    text = models.TextField()

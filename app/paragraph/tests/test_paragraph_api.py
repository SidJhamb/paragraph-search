"""
Tests for the paragraphs API.
"""
import mock.mock
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from mock import patch

from rest_framework import status
from rest_framework.test import APIClient
#from paragraph.views import get_paragraph
from unittest.mock import MagicMock, patch

from core.models import (
    Paragraph,
)

from paragraph.serializers import ParagraphSerializer
from paragraph.views import DictionaryRetrieveView

PARAGRAPHS_LIST_URL = reverse('paragraph:paragraph-list')
PARAGRAPHS_POST_URL = reverse('paragraph:create')
DICTIONARY_FETCH_URL = reverse('paragraph:dict')

MOCK_RESPONSE = {
    "this": "The definition for word \'this\'",
    "test": "The definition for word \'test\'",
    "paragraph": "The definition for word \'paragraph\'",
}


def create_paragraph(text):
    """Create and return a sample recipe."""
    paragraph = Paragraph.objects.create(text=text)
    return paragraph.id


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_paragraph_list(self):
        """Test auth is required to call paragraphs List API."""
        res = self.client.get(PARAGRAPHS_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_paragraph_create(self):
        """Test auth is required to call paragraphs create API."""
        res = self.client.post(PARAGRAPHS_POST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_dictionary_fetch(self):
        """Test auth is required to call paragraphs create API."""
        res = self.client.post(DICTIONARY_FETCH_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateParagraphApiTests(TestCase):
    """Test authenticated paragraph API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_paragraphs_or_operator(self):
        """Test retrieving a list of paragraphs."""
        p1_id = create_paragraph("This is a test paragraph")
        p2_id = create_paragraph("This is another sample paragraph")

        params = {'words': f'{"test"},{"another"}', 'operator': f'{"or"}'}
        res = self.client.get(PARAGRAPHS_LIST_URL, params)

        paragraphs = Paragraph.objects.all()
        serializer = ParagraphSerializer(paragraphs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_paragraphs_and_operator(self):
        """Test retrieving a list of paragraphs."""
        p1_id = create_paragraph("This is a test paragraph")
        p2_id = create_paragraph("This is another sample paragraph")

        params = {'words': f'{"test"},{"paragraph"}', 'operator': f'{"and"}'}
        res = self.client.get(PARAGRAPHS_LIST_URL, params)

        paragraphs = Paragraph.objects.filter(id=p1_id)
        serializer = ParagraphSerializer(paragraphs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_paragraphs_single_word(self):
        """Test retrieving a list of paragraphs."""
        p1_id = create_paragraph("This is a test paragraph")
        p2_id = create_paragraph("This is another sample paragraph")

        params = {'words': f'{"test"}', 'operator': f'{"and"}'}
        res = self.client.get(PARAGRAPHS_LIST_URL, params)

        paragraphs = Paragraph.objects.filter(id=p1_id)
        serializer = ParagraphSerializer(paragraphs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

        params = {'words': f'{"sample"}', 'operator': f'{"or"}'}
        res = self.client.get(PARAGRAPHS_LIST_URL, params)

        paragraphs = Paragraph.objects.filter(id=p2_id)
        serializer = ParagraphSerializer(paragraphs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    @mock.mock.patch('paragraph.api_client.get_paragraph', return_value="text")
    def test_create_paragraph_success(self, mock_response):
        res = self.client.post(PARAGRAPHS_POST_URL)
        paragraph = Paragraph.objects.get(id=1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(paragraph.text, "text")

    @mock.mock.patch('paragraph.api_client.get_paragraph', return_value=None)
    def test_create_paragraph_failure(self, mock_response):
        res = self.client.post(PARAGRAPHS_POST_URL)
        self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("paragraph.api_client.get_word_definition")
    def test_retrieve_dictionary_success(self, mock_response):
        def side_effect(word):
            if word == "this":
                return "The definition for word \'this\'"
            elif word == "test":
                return "The definition for word \'test\'"
            elif word == "paragraph":
                return "The definition for word \'paragraph\'"

        mock_response.side_effect = side_effect

        create_paragraph("this this test paragraph")
        create_paragraph("this test paragraph")
        res = self.client.get(DICTIONARY_FETCH_URL)
        self.assertEqual(res.data, MOCK_RESPONSE)

    def test_retrieve_dictionary_common_words(self):
        create_paragraph("this this test paragraph")
        create_paragraph("this test paragraph")
        words = DictionaryRetrieveView._get_common_words(10)
        self.assertEqual(words[0], ('this', 3))
        self.assertEqual(words[1], ('test', 2))
        self.assertEqual(words[2], ('paragraph', 2))


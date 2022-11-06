"""
Tests for the paragraphs API.
"""
import mock.mock
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

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


class ParagraphCreateApiTest(TestCase):
    """Test the dictionary create API."""

    def setUp(self):
        self.client = APIClient()

    @mock.mock.patch('paragraph.api_client.get_paragraph', return_value="text")
    def test_create_paragraph_success(self, mock_response):
        res = self.client.get(PARAGRAPHS_POST_URL)
        paragraph = Paragraph.objects.first()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(paragraph.text, "text")

    @mock.mock.patch('paragraph.api_client.get_paragraph', side_effect=Exception("error"))
    def test_create_paragraph_failure(self, mock_response):
        res = self.client.get(PARAGRAPHS_POST_URL)
        self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(res.json(), {'error': 'error'})


class DictionaryApiTest(TestCase):
    """Test the dictionary get API."""

    def setUp(self):
        self.client = APIClient()

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

    @patch("paragraph.api_client.get_word_definition", side_effect=Exception("error"))
    def test_retrieve_dictionary_failure(self, mock_response):
        create_paragraph("this this test paragraph")
        create_paragraph("this test paragraph")
        res = self.client.get(DICTIONARY_FETCH_URL)
        self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(res.json(), {'error': 'error'})

    def test_retrieve_dictionary_common_words(self):
        create_paragraph("this this test paragraph")
        create_paragraph("this test paragraph")
        words = DictionaryRetrieveView._get_common_words(10)
        self.assertEqual(words[0], ('this', 3))
        self.assertEqual(words[1], ('test', 2))
        self.assertEqual(words[2], ('paragraph', 2))


class ParagraphSearchApiTests(TestCase):
    """Test the paragraph search API."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_all_paragraphs(self):
        create_paragraph("This is a test paragraph")
        create_paragraph("This is another sample paragraph")

        res = self.client.get(PARAGRAPHS_LIST_URL)

        paragraphs = Paragraph.objects.all()
        serializer = ParagraphSerializer(paragraphs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_paragraphs_bad_request(self):
        create_paragraph("This is a test paragraph")
        create_paragraph("This is another sample paragraph")

        params = {'words': f'{"test"},{"another"}'}
        res = self.client.get(PARAGRAPHS_LIST_URL, params)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_paragraphs_or_operator(self):
        create_paragraph("This is a test paragraph")
        create_paragraph("This is another sample paragraph")

        params = {'words': f'{"test"},{"another"}', 'operator': f'{"or"}'}
        res = self.client.get(PARAGRAPHS_LIST_URL, params)

        paragraphs = Paragraph.objects.all()
        serializer = ParagraphSerializer(paragraphs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_paragraphs_and_operator(self):
        """Test retrieving a list of paragraphs."""
        p1_id = create_paragraph("This is a test paragraph")
        create_paragraph("This is another sample paragraph")

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

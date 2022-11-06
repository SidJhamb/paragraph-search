"""
Views for the paragraph APIs
"""
import re
from collections import Counter

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    ListAPIView
)
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)

from core.models import (
    Paragraph
)
from paragraph import (
    serializers,
    api_client
)


class ParagraphCreateView(CreateAPIView):
    """View for creating paragraphs."""
    queryset = Paragraph.objects.all()
    serializer_class = serializers.ParagraphSerializer

    def create(self, request, *args, **kwargs):
        """Create new paragraph record for the authenticated user."""
        try:
            response_text = api_client.get_paragraph()
        except Exception as err:
            return Response(data={"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(data={"text": response_text})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DictionaryRetrieveView(RetrieveAPIView):
    """View for retrieving definition of the most common words present in the database."""
    queryset = Paragraph.objects.all()
    serializer_class = serializers.ParagraphSerializer

    @staticmethod
    def _get_common_words(max_count):
        counter = Counter()

        for paragraph_text in Paragraph.objects.all():
            words = re.findall(r'\w+', paragraph_text.text)
            counter += Counter(dict(Counter(words).most_common(max_count)))

        return counter.most_common(10)

    @staticmethod
    def _populate_response(common_words):
        response = {}
        for word, count in common_words:
            response[word] = api_client.get_word_definition(word)
        return response

    def get(self, request, *args, **kwargs):
        """Get response for the authenticated user."""
        common_words = self._get_common_words(max_count=10)
        try:
            response = self._populate_response(common_words)
        except Exception as err:
            return Response(data={"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'words',
                OpenApiTypes.STR,
                description='Comma separated list of words to filter.',
            ),
            OpenApiParameter(
                'operator',
                OpenApiTypes.STR,
                description='Operator to use for filtering.',
            ),
        ]
    )
)
class ParagraphListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Retrieve paragraphs from the database based on the search query."""
    serializer_class = serializers.ParagraphSerializer
    queryset = Paragraph.objects.all()

    @staticmethod
    def _populate_search_query(words, operator):
        query = ""

        if operator == "or":
            for word in words:
                query += word + " | "
            query = query.removesuffix(" | ")
        else:
            for word in words:
                query += word + " & "
            query = query.removesuffix(" & ")

        return SearchQuery(query, search_type="raw")

    def get_queryset(self):
        """Filter queryset for the authenticated user."""
        word_filter_present = False
        operator_filter_present = False

        if 'words' in self.request.query_params:
            word_filter_present = True
            words = self.request.query_params.get('words').split(',')

        if 'operator' in self.request.query_params:
            operator_filter_present = True
            operator = self.request.query_params.get('operator')

        if word_filter_present and operator_filter_present:
            search_query = self._populate_search_query(words, operator)
            return Paragraph.objects.annotate(search=SearchVector('text')).filter(search=search_query)

        if not word_filter_present and not operator_filter_present:
            return Paragraph.objects.all()

        raise ValidationError(detail='Incomplete search query parameters.')

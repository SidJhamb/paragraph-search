"""
Views for the recipe APIs
"""
import requests
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
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.postgres.search import SearchQuery, SearchVector

from core.models import (
    Paragraph
)
from paragraph import serializers


class ParagraphCreateView(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Paragraph.objects.all()
    serializer_class = serializers.ParagraphSerializer

    def create(self, request, *args, **kwargs):
        response = requests.request("GET", "http://metaphorpsum.com/paragraphs/1/50")
        serializer = self.get_serializer(data={"text": response.text})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ParagraphRetrieveView(RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Paragraph.objects.all()
    serializer_class = serializers.ParagraphSerializer


class ParagraphListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage tags in the database."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ParagraphSerializer
    queryset = Paragraph.objects.all()
    # filter_backends = [filters.SearchFilter]
    # filter_backends = (FullWordSearchFilter, )
    # search_fields = ['id']
    # word_fields = ('text',)

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        words = self.request.query_params.get('words').split(',')
        operator = self.request.query_params.get('operator')
        query = ""

        if operator == "or":
            for word in words:
                query += word + " | "
            query = query.removesuffix(" | ")
        else:
            for word in words:
                query += word + " & "
            query = query.removesuffix(" & ")

        print("query")
        print(query)

        search_query = SearchQuery(query, search_type="raw")
        # return Paragraph.objects.filter(text__contains=word)
        # return Paragraph.objects.filter(id__in=ids)
        return Paragraph.objects.annotate(search=SearchVector('text')).filter(search=search_query)
        # return Paragraph.objects.all()
        # return Paragraph.objects.filter(text__search=word)

"""
Views for the user API.
"""
import requests

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

@api_view(['GET'])
@authentication_classes((authentication.TokenAuthentication,))
@permission_classes((permissions.IsAuthenticated,))
def hello_world(request):
    response = requests.request("GET", "http://metaphorpsum.com/paragraphs/1")
    return Response({"message": response})


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user

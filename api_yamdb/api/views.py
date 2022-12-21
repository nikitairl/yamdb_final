from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import ADMIN, MODERATOR, User

from .filters import TitleFilter
from .permissions import AdminModeratorAuthor, AdminOnly, IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleReadOnlySerializer, TitleSerializer,
                          UserSerializer)


class CreateListDestroyViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet
):
    """Intermediate class to perform CRUD"""
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    """Gets Categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """Gets Genres."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Gets Titles."""
    queryset = Title.objects.all().annotate(
        rating=Avg("reviews__score"))
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleSerializer
        return TitleReadOnlySerializer


class UserViewSet(viewsets.ModelViewSet):
    """User viewset."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,))
    def users_profile(self, request):
        user = get_object_or_404(
            User,
            username=request.user.username)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(
            user,
            context={'request': request},
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if self.request.user.role in [ADMIN, MODERATOR]:
            serializer.save()
        else:
            serializer.save(role=user.role)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK)


class APISignUp(APIView):
    """
    Allows anyone to get the Token via email with using only email+username
    for example:
    {
        "email": "str"
        "username": "str"
    }
    """
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = request.data

        email_body = (
            f'Hello, {user.username}, here is your Token: {user.password}'
        )
        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Your API.'
        }
        self.send_email(data)
        return Response(serializer.data, status=200)


class GetToken(APIView):
    """
    {
        "username": "str"
        "token": "str"
    }
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            token = RefreshToken.for_user(user).access_token
            return Response(
                {"token": str(token)},
                status=status.HTTP_201_CREATED
            )
        return Response({"field_name": ['confirmation_code']},
                        status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(ModelViewSet):
    """Gets Comments."""
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthor,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(ModelViewSet):
    """Gets Reviews."""
    permission_classes = (AdminModeratorAuthor,)
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(title=title, author=self.request.user)

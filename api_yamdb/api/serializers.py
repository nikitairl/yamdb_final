from datetime import datetime

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator, ValidationError
from reviews.models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    """Converts Category data."""
    slug = serializers.SlugField(
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Converts Genre data."""
    slug = serializers.SlugField(
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Converts Title data."""
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year = datetime.now().year
        if year < value:
            raise serializers.ValidationError('Check the year')
        return value


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """Converts ReadOnlyTitle data."""
    rating = serializers.IntegerField()
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = "__all__"
        read_only_fields = ('id', 'name', 'year', 'description', 'rating')


class SignUpSerializer(serializers.ModelSerializer):
    """Converts data while signing up"""

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя!'
            )
        if User.objects.filter(
            username=username
        ).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        return username


class GetTokenSerializer(serializers.ModelSerializer):
    """Converts data while getting Token."""
    username = serializers.CharField(
        required=True)
    confirmation_code = serializers.CharField(
        required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class ReviewSerializer(serializers.ModelSerializer):
    """Converts Review data."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST' and Review.objects.filter(
            title=title,
            author=request.user
        ).exists():
            raise ValidationError(
                'You have already written a review'
            )
        return data

    def validate_score(self, score):
        if score < 1 or score > 10:
            raise serializers.ValidationError(
                'The score has to be from 1 to 10'
            )
        return score

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Converts Comment data."""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    """Converts User data."""
    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User

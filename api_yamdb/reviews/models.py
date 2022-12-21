from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Genre(models.Model):
    """Describes Genres."""
    name = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name='Название жанра',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор жанра',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Describes Categories."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор категории'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Describes Titels."""
    name = models.CharField(
        max_length=100,
        null=False,
        verbose_name='Название произведения',
    )
    year = models.IntegerField(
        verbose_name='Дата выхода произведения',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанры произведения',
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория произведения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведние'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Intermediary Model."""
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} belongs to {self.genre}'


class Review(models.Model):
    """Describes Reviews."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведние'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(10)],
        verbose_name='Оценка произведения'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]

    def __str__(self):
        return f'{self.title}, {self.score}, {self.author}'


class Comment(models.Model):
    """Describes Comments."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.CharField(
        'Текст комментария',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]

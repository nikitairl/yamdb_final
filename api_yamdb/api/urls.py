from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (APISignUp, CategoryViewSet, CommentViewSet, GenreViewSet,
                    GetToken, ReviewViewSet, TitleViewSet, UserViewSet)

app_name = 'api'

router = SimpleRouter()

router.register(
    'categories',
    CategoryViewSet,
    basename='сategories'
)

router.register(
    'genres',
    GenreViewSet,
    basename='genres'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='review'
)
router.register('titles', TitleViewSet, basename='titles')
router.register('users', UserViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include([
        path('token/', GetToken.as_view(), name='get_token'),
        path('signup/', APISignUp.as_view(), name='signup')
    ]))
]

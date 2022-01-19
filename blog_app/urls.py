from django.urls import path
from . import views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    add_comment,
    make_private,
    make_public
)


urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user_posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('about/', views.about, name='about'),
    path('post/<int:pk>/private/', make_private, name='post_private'),
    path('post/<int:pk>/public/', make_public, name='post_public'),
    path('post/<int:pk>/comment/', add_comment, name='add_comment'),
    path('post/calendar/', views.CalendarView.as_view(), name='calendar'), # here

    # path('post/<int:pk>/comment/', add_comment, name='add_comment'),
]

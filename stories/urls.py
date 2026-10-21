from django.contrib.auth import views as auth_views
from django.urls import path

from . import api, views

app_name = 'stories'

urlpatterns = [
    path('', views.index, name='index'),
    path('kids/', views.kids, name='kids'),
    path('adults/', views.adults, name='adults'),
    path('search/', views.search, name='search'),
    path('genre/<slug:slug>/', views.genre_list, name='genre_list'),
    path('story/<slug:slug>/', views.story_detail, name='detail'),
    path('story/<slug:slug>/bookmark/', views.toggle_bookmark, name='bookmark'),
    path('saved/', views.bookmarks, name='bookmarks'),

    path('age-gate/', views.age_gate, name='age_gate'),
    path('kids-mode/', views.kids_mode, name='kids_mode'),

    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='stories/login.html', redirect_authenticated_user=True), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.register, name='register'),

    path('api/stories/', api.StoryListAPI.as_view(), name='api_stories'),
    path('api/stories/<slug:slug>/', api.StoryDetailAPI.as_view(), name='api_story'),
    path('api/genres/', api.GenreListAPI.as_view(), name='api_genres'),
]

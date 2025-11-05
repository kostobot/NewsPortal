from django.urls import path
# Импортируем созданное нами представление
from .views import (
   PostList, PostDetail, SearchPosts, NewsCreate, NewsUpdate, 
   NewsDelete, ArticleCreate, ArticleUpdate, ArticleDelete, PostLikeView, PostDislikeView, PostsCategories, add_subscribe, 
   CategoryPostsView, 
)


urlpatterns = [
   path('', PostList.as_view(), name='posts_list'),
   path('<int:pk>', PostDetail.as_view(), name='post_detail'),
   path('search/', SearchPosts.as_view(), name='search_posts'),
   path('news/create/', NewsCreate.as_view(), name='news_create'),
   path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_update'),
   path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
   path('articles/create/', ArticleCreate.as_view(), name='article_create'),
   path('articles/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_update'),
   path('articles/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
   path('post/<int:pk>/like/', PostLikeView.as_view(), name='post_like'),
   path('post/<int:pk>/dislike/', PostDislikeView.as_view(), name='post_dislike'),
   path('categories/', PostsCategories.as_view(), name='categories'),
   path('categories/<int:pk>/', CategoryPostsView.as_view(), name='category_posts'),
   path('categories/<int:pk>/subscribe/', add_subscribe, name='add_subscribe'),
]
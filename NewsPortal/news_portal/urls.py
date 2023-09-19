from django.urls import path, include
from .views import NewsList, NewsDetail, NewsCreate, ArticleCreate, NewsUpdate, ArticleUpdate, NewsDelete, ArticleDelete, CategoryListView, upgrade_me, subscribe
from django.views.decorators.cache import cache_page

urlpatterns = [
   path('', (NewsList.as_view()), name='news_list'),
   path('<int:pk>/', (NewsDetail.as_view()), name='news_detail'),
   path('create/', NewsCreate.as_view(), name='news_create'),
   path('article/create/', ArticleCreate.as_view(), name='article_create'),
   path('<int:pk>/update/', NewsUpdate.as_view(), name='news_update'),
   path('article/<int:pk>/update/', ArticleUpdate.as_view(), name='article_update'),
   path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
   path('article/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
   path('upgrade/', upgrade_me, name = 'upgrade'),
   path('categories/<int:pk>', CategoryListView.as_view(), name='category-list'),
   path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
]




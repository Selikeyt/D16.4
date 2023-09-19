from django.forms import DateInput
from django_filters import FilterSet, ModelChoiceFilter
from django_filters import DateFilter
from .models import Post, Author, Category

class PostFilter(FilterSet):
   author = ModelChoiceFilter(field_name='author', queryset=Author.objects.all(), label='Author', empty_label='любой')
   date = DateFilter(field_name='post_time_in', widget=DateInput(attrs={'type': 'date'}),
                      label='Поиск по дате',
                      lookup_expr='date__gt')

   class Meta:
       model = Post
       fields = {
           'author': ['exact'],
           # 'category': ['exact'],
           'title': ['icontains'],
       }
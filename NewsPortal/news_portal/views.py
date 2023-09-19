from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from django.core.mail import EmailMultiAlternatives
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .tasks import send_email_task
from django.core.cache import cache

from .forms import NewsForm
from .models import Post, Category
from .filters import PostFilter

class PostTypeException(Exception):
    pass

class NewsList(ListView):
    model = Post
    ordering = '-post_time_in'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

class NewsDetail(DetailView):
    model = Post
    template_name = "post.html"
    context_object_name = 'post'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'news-{self.kwargs["pk"]}', None)

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'news-{self.kwargs["pk"]}', obj)

        return obj

class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news_portal.add_post'
    form_class = NewsForm
    model = Post
    template_name = 'news_edit.html'


    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NS'
        post.save()
        send_email_task.delay(post.pk)
        return super().form_valid(form)

class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news_portal.add_post'
    form_class = NewsForm
    model = Post
    template_name = 'article_edit.html'


    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AC'
        post.save()
        send_email_task.delay(post.pk)
        return super().form_valid(form)

class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'news_portal.change_post'
    form_class = NewsForm
    model = Post
    template_name = 'news_edit.html'


    def form_valid(self, form):
        post = form.save(commit=False)
        if post.type == 'AC':
            return HttpResponse('Такой статьи не существует')
        post.save()
        return super().form_valid(form)

    class ProtectedView(LoginRequiredMixin, TemplateView):
        template_name = 'news_edit.html'

class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'news_portal.change_post'
    form_class = NewsForm
    model = Post
    template_name = 'article_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if post.type == 'NS':
            return HttpResponse('Такой новости не существует')
        post.save()
        return super().form_valid(form)

    class ProtectedView(LoginRequiredMixin, TemplateView):
        template_name = 'article_edit.html'

class NewsDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('news_list')
    template_name = 'news_delete.html'


class ArticleDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('news_list')
    template_name = 'article_delete.html'

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('news_list')

class CategoryListView(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-post_time_in')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    html_content = render_to_string(
        'send_email.html',
        {
            'category': category.name,
        }
    )

    msg = EmailMultiAlternatives(
        subject=f'{user} {category.name}',
        body=category.name,
        from_email='seafoamskl@yandex.ru',
        to=['skl.74@mail.ru'],
    )
    msg.attach_alternative(html_content, "text/html")

    msg.send()

    message = 'Вы подписались на рассылку новостей категории'
    return render(request, 'subscribe.html', {'category': category, 'message': message})

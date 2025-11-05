from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View,
    )
from django.shortcuts import get_object_or_404, redirect

from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string


class PostList(ListView):
    model = Post
    ordering = '-date_time'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['total_posts'] = self.get_queryset().count()
        return context
    
class PostsCategories(ListView):
    model = Category
    template_name = 'posts_categories.html'
    context_object_name = 'categories'

class CategoryPostsView(ListView):
    model = Post
    template_name = 'category_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        return Post.objects.filter(category=self.category).order_by('-date_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        
        return context

class PostLikeView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.like()
        return redirect(post.get_absolute_url())
    
class PostDislikeView(View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.dislike()
        return redirect(post.get_absolute_url())
    
class SearchPosts(ListView):
    """ Представление всех постов в виде списка. """
    paginate_by = 3
    model = Post
    ordering = 'date_time'
    template_name = 'search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        """ Переопределяем функцию получения списка статей. """
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs) -> dict:
        """ Метод get_context_data позволяет изменить набор данных, который будет передан в шаблон. """
        context = super().get_context_data(**kwargs)
        context['search_filter'] = self.filterset
        context['total_posts'] = self.filterset.qs.count()
        return context

class PostCreateBase(PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = 'blog.add_post'
    post_type = None
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        author = self.request.user.author
        context['daily_limit'] = author.daily_post_limit
        if hasattr(self, 'limit_reached'):
            context['limit_reached'] = self.limit_reached
        else:
            context['limit_reached'] = False

        return context

    def form_valid(self, form):
        author = self.request.user.author

        # проверка лимита публикаций
        if author.posts_today_count(self.post_type) >= author.daily_post_limit:
            # передаем флаг в контекст через экземпляр
            self.limit_reached = True
            return self.form_invalid(form)

        form.instance.author = author
        form.instance.post_type = self.post_type
        return super().form_valid(form)


class NewsCreate(PostCreateBase):
    post_type = Post.NEWS
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = 'blog.add_post'
        
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Добавить новость"
        return context
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.NEWS
        return super().form_valid(form)
    
class NewsUpdate(PermissionRequiredMixin, UpdateView):
    """ Представление для редактирования новости. """
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = 'blog.change_post'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Редактировать новость"
        return context

class NewsDelete(PermissionRequiredMixin, DeleteView):
    """ Представление для удаления новости. """
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')
    permission_required = 'blog.delete_post'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Удалить новость"
        context['previous_page_url'] = reverse_lazy('posts_list')
        return context


class ArticleCreate(PostCreateBase):
    """ Представление для создания статьи. """
    post_type = Post.ARTICLE
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = 'blog.add_post'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Добавить статью"
        return context
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.ARTICLE
        return super().form_valid(form)
    
class ArticleUpdate(PermissionRequiredMixin, UpdateView):
    """ Представление для редактирования статьи. """
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = 'blog.change_post'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Редактировать статью"
        return context
    

class ArticleDelete(PermissionRequiredMixin, DeleteView):
    """ Представление для удаления статьи. """
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')
    permission_required = 'blog.delete_post'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Удалить статью"
        context['previous_page_url'] = reverse_lazy('posts_list')
        return context
    
    
class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

@login_required 
def add_subscribe(request, pk):
    user = request.user
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    
    text_content = f'Здравствуй, {user.username} ! Вы подписались на категорию "{category.name}". '
    f'Теперь вы будете одним из первых узнавать о новостях из этой категории!'
    html_content = render_to_string('add_subscribe.html', {'username': user.username, 'category': category.name})
    
    msg = EmailMultiAlternatives(
        subject=f'News Portal: {category.name}',
        body=text_content,
        from_email='News Portal <kastetpsy@yandex.ru>',
        to=[user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
    return redirect('category_posts', pk=pk)
    
    
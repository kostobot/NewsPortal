from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
    )
from .models import Post
from .filters import PostFilter
from .forms import PostForm

class PostList(ListView):
    model = Post
    ordering = '-date_time'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = self.get_queryset().count()  # 👈 добавляем общее число постов
        return context

    
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

class NewsCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Добавить новость"
        return context
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.NEWS
        return super().form_valid(form)
    
class NewsUpdate(UpdateView):
    """ Представление для редактирования новости. """
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Редактировать новость"
        return context

class NewsDelete(DeleteView):
    """ Представление для удаления новости. """
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Удалить новость"
        context['previous_page_url'] = reverse_lazy('posts_list')
        return context


class ArticleCreate(CreateView):
    """ Представление для создания статьи. """
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Добавить статью"
        return context
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.ARTICLE
        return super().form_valid(form)
    
class ArticleUpdate(UpdateView):
    """ Представление для редактирования статьи. """
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Редактировать статью"
        return context
    

class ArticleDelete(DeleteView):
    """ Представление для удаления статьи. """
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Удалить статью"
        context['previous_page_url'] = reverse_lazy('posts_list')
        return context
    
    
class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
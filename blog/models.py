from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=0)
    daily_post_limit = models.SmallIntegerField(default=3)

    def posts_today_count(self, post_type):
        now = timezone.localtime()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return self.posts.filter(
            post_type=post_type,
            date_time__range=(today_start, today_end)
        ).count()

    def can_post_today(self, post_type):
        return self.posts_today_count(post_type) < self.daily_post_limit

    def __repr__(self):
        return f"Author (user.name='{self.user}', rating='{self.rating}')"
    
    def __str__(self):
        return f"{self.user}"

    def update_rating(self):
        posts_rating = self.posts.aggregate(result=Sum('rating')).get('result')
        comments_rating = self.user.comments.aggregate(result=Sum('rating')).get('result')
        self.rating = 3 * posts_rating + comments_rating
        self.save()
        print(f"Рейтинг = 3 * {posts_rating} + {comments_rating} = {self.rating}")

class Category(models.Model):
    name = models.CharField(unique=True, max_length=256)
    subscribers = models.ManyToManyField(User, related_name='categories', blank=True)

    def __repr__(self):
        return f"Category (name='{self.name}')"

    def __str__(self):
        return f"{self.name}"

class Post(models.Model):
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    date_time = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=500)
    text = models.TextField()
    _rating = models.SmallIntegerField(default=0, db_column='rating')
    url_img = models.URLField(blank=True, max_length=500)

    @property
    def rating(self):
        return self._rating
    
    @rating.setter
    def rating(self, value):
        self._rating = int(value) if value >= 0 else 0
        return self.save()
    
    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self, length=128):
        return f'{self.text[:length]}...' if len(self.text) > length else self.text 
    
    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.title}'
    
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.category} | {self.post}'
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
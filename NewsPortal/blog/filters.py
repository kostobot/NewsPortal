from django_filters import (
    FilterSet, CharFilter, DateFilter
)

from django import forms


class PostFilter(FilterSet):
    title = CharFilter(
        field_name='title', 
        label='Заголовок содержит', 
        lookup_expr='icontains',
    )
    
    author__user__username = CharFilter(
        field_name='author__user__username', 
        lookup_expr='icontains',
        label='Имя автора',
    )
    
    date_time__gt = DateFilter(
        field_name="date_time", label="От даты", lookup_expr='gt', widget = forms.DateInput(attrs={'type':'date'})
    )
    
    class Meta:
        fields = ['title', 'author__user__username', 'date_time__gt']
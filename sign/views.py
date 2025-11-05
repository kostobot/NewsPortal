from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm, UpdateProfile
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from .signals import user_registered

class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'
    
    def form_valid(self, form):
      form.save()
      user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
      login(self.request, user)
      user_registered.send(sender=self.__class__, user=user)
      return HttpResponseRedirect("/sign/account/")
    
@login_required
def make_author(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return HttpResponseRedirect("/sign/account/")

class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'sign/account.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context
    
class UpdateProfile(LoginRequiredMixin, UpdateView):
  model = User
  form_class = UpdateProfile
  success_url = '/'

  def setup(self, request, *args, **kwargs):
    self.user_id = request.user.pk
    return super().setup(request, *args, **kwargs)

  def get_object(self, queryset=None):
    if not queryset:
      queryset = self.get_queryset()
    return get_object_or_404(queryset, pk=self.user_id)
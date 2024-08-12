from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView,DeleteView,FormView
from .models import Task
from django.urls import reverse_lazy


from django.contrib.auth.views import LoginView
#reverse lazy is used tp send the url form one page to another

# Create your views here.


from django.contrib.auth.mixins import LoginRequiredMixin

#this login mixin will ensure that if the user is authenticated then only him to access the data otherwise send to the page where we wanted, wherever
# we will put this it will first ensure the above thing

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

class CustomLoginView(LoginView):
    template_name='base/login.html'
    fields='__all__'
    redirect_authenticated_user=True

    def get_success_url(self) -> str:
        return reverse_lazy('tasks')
    

class RegisterPage(FormView):
    template_name='base/register.html'
    form_class=UserCreationForm
    redirect_authenticated_user=True
    success_url=reverse_lazy('tasks')

    def form_valid(self, form: Any) -> HttpResponse:
        user=form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage,self).form_valid(form)

    def get(self,*args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')  
        return super(RegisterPage,self).get(*args, **kwargs)  


class TaskList(LoginRequiredMixin,ListView):
    model=Task
    context_object_name='tasks'


# we used this to override the context data which returns the or contains all data passed to the app 
# in this functionality we are disallowing one user to see posts or work of another user    


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context= super().get_context_data(**kwargs)
        context['tasks']=context['tasks'].filter(user=self.request.user)
        context['count']=context['tasks'].filter(complete=False).count()
    
        search_input=self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks']=context['tasks'].filter(title__icontains=search_input)        
        return context


class TaskDetail(LoginRequiredMixin,DetailView):
    model=Task
    context_object_name='task'
    template_name='base/task.html'    

class TaskCreate(LoginRequiredMixin,CreateView):
    model=Task

        # earlier from one account more than one users were able to create the post but it shouldn;t since one particular user has logged so to avoid this in fields we have removed
    # the users part and set onluy required

    fields=['title','description','complete']
    success_url=reverse_lazy('tasks')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user=self.request.user
        return super(TaskCreate,self).form_valid(form)

class TaskUpdate(LoginRequiredMixin,UpdateView):
    model=Task


    fields=['title','description','complete']
    success_url=reverse_lazy('tasks')        


class DeleteView(LoginRequiredMixin,DeleteView):
    model=Task
    context_object_name='task'
    success_url=reverse_lazy('tasks')

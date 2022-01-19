import calendar
from cmath import pi
from django import http
from django.core.mail import message
from django.http import request
from .models import Post, Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import date, datetime, timedelta
from django.db.models import Q, F
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm, CommentForm
from django.core.exceptions import ValidationError
import requests
from PIL import Image
from io import StringIO
from urllib.request import urlopen

from .utils import Calendar
from django.utils.safestring import mark_safe

from django.db import models

from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)


class PostListView(ListView):
    model = Post
    template_name = 'blog_app/index.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        try:
            keyword = self.request.GET['q']
        except:
            keyword = ''
        if (keyword != ''):
            object_list = self.model.objects.filter(
                Q(content__icontains=keyword) | Q(title__icontains=keyword), delete_status = False)
        else:
            object_list = self.model.objects.filter(delete_status = False)
            # print(object_list)
        return object_list


class UserPostListView(ListView):
    model = Post
    template_name = 'blog_app/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        
        if self.request.user.is_superuser:
            return Post.objects.filter(author=user, delete_status = False).order_by('-date_posted')
        if user == self.request.user:
            return Post.objects.filter(author=user, delete_status = False).order_by('-date_posted')
        else:
            return Post.objects.filter(author=user, private = False, delete_status = False).order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user

        try:
            f = urlopen(self.request.POST.get('image_link'))
            # Image.open(self.request.POST.get('image_link'))
            imageFound = True
        except:
            messages.warning(request, 'Sorry, your image is invalid')
            imageFound = False
            return redirect('post_create')
        
    #     try:
    #         ticket_attachmet_image = self.request.POST.get('image_link')
    #     except:
    #         ticket_attachmet_image = None

    #    # check if uploaded image is valid (for example not video file ) .
    #     if not ticket_attachmet_image == None:
    #         try:
    #             r = requests.get(ticket_attachmet_image)
    #             print(r.content)
    #             im = Image.open(StringIO(r.content))
    #             # Image.open(ticket_attachmet_image)
    #         except:
    #             # messages.warning(request, 'sorry, your image is invalid')
    #             print('ERORRRRRRRRRo')
    #             return redirect('post_create')

        # r = requests.head(self.request.POST.get('image_link'))

        # print('------------------')
        # print(r, self.request.POST.get('image_link'))
        # if r.status_code == 404:
        #     print('It doesn\'t exist!')
        # print('--------------')
        # print(request.POST.get('image_link'))

        return super().form_valid(form)
    
    # def save_details(self, form, request):
    #     self.form_valid(self, form)

    #     if request.method == 'POST':
    #         print('HERE')


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'image_link']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser:
            return True
        return False
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     image = cleaned_data.get("image")
    #     image_link = cleaned_data.get("image_link")

    #     if image and image_link:
    #         raise ValidationError("Only one field can be fill at a time.")
    #     elif not image and not image_link:
    #         raise ValidationError("Fill a Image link or upload a Image/Gif/Video")
      
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def form_valid(self, form):
        success_url = self.get_success_url()
        # self.object.delete()
        self.object.delete_status = True
        self.object.save()
        return HttpResponseRedirect(success_url)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser:
            return True
        return False

def about(request):
    return render(request, 'blog_app/about.html', {'title': 'About'})


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        user = User.objects.get(id=request.POST.get('user_id'))
        text = request.POST.get('text')
        
        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except:
            parent_id = None

        if parent_id:
            parent_obj = Comment.objects.get(id=parent_id)
            if parent_obj:
                Comment(author = user, post = post, text = text, parent_id = parent_id).save()
        else:
            Comment(author=user, post=post, text=text).save()

        messages.success(request, "Your comment has been added successfully.")
    else:
        return redirect('post_detail', pk=pk)
    return redirect('post_detail', pk=pk)


@login_required
def make_private(request, pk):
    post = get_object_or_404(Post, pk=pk)
  
    post.private = True
    post.save()
    messages.success(request, "Your Blog has been successfully Private.")
  
    return redirect('post_detail', pk=pk)

@login_required
def make_public(request, pk):
    post = get_object_or_404(Post, pk=pk)

    post.private = False
    post.save()
    messages.success(request, "Your Blog has been successfully Public.")
    
    return redirect('post_detail', pk=pk)


class CalendarView(ListView):
    model = Post
    template_name = 'blog_app/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))

        # Instantiate our calendar class with today's year and date
        cal = Calendar(d, d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth()
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month
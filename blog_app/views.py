from django import http
from django.core.mail import message
from django.http import request
from .models import Post, Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import datetime
from django.db.models import Q, F
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm, CommentForm
from django.core.exceptions import ValidationError

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
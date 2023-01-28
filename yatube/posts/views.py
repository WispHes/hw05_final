from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def get_page(page_number, post_list):
    paginator = Paginator(post_list, settings.COUNT_POST)
    return paginator.get_page(page_number)


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    text = 'Это главная страница проекта Yatube'
    posts = (
        Post.objects.select_related('author', 'group')
    )
    page_number = request.GET.get('page')
    page_obj = get_page(page_number, posts)
    context = {
        'title': title,
        'text': text,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = f'Записи сообщества {slug}'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_number = request.GET.get('page')
    page_obj = get_page(page_number, posts)
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    profile = get_object_or_404(User, username=username)
    post = profile.posts.select_related('group')
    page_number = request.GET.get('page')
    page_obj = get_page(page_number, post)
    following = (
        request.user.is_authenticated
        and profile.following.filter(user=request.user).exists()
    )
    context = {
        'profile': profile,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    detail = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    comments = detail.comments.select_related('author')
    context = {
        'detail': detail,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post_edit = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    if request.user != post_edit.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_edit,
        is_edit=True
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(
        author__following__user=request.user)
    page_number = request.GET.get('page')
    page_obj = get_page(page_number, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user_author = get_object_or_404(User, username=username)
    if user_author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=user_author
        )
    return redirect('posts:profile', user_author)


@login_required
def profile_unfollow(request, username):
    user_follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    user_follower.delete()
    return redirect('posts:profile', username)

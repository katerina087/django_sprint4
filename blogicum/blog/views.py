from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Category, Post, Comment
from .forms import UserForm, PostForm, CommentForm


# Вспомогательные функции
def get_posts_with_comments(**kwargs):
    """Получение постов с количеством комментариев"""
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).annotate(
        comment_count=Count('comments')
    ).filter(**kwargs).order_by('-pub_date')


def get_paginated_page(request, queryset, items_per_page=10):
    """Вычисление страницы пагинатора"""
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Главная страница"""
    posts = get_posts_with_comments(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )

    page_obj = get_paginated_page(request, posts)
    context = {'page_obj': page_obj}
    return render(request, "blog/index.html", context)


def post_detail(request, post_id):
    """Отображение полного описания выбранной публикации"""
    posts = get_posts_with_comments(id=post_id)

    if request.user.is_authenticated:
        # Для авторизованных пользователей
        post = get_object_or_404(posts, id=post_id)
        if request.user != post.author:
            # Если не автор, проверяем публикацию
            post = get_object_or_404(
                posts,
                id=post_id,
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
    else:
        # Для анонимных пользователей только опубликованное
        post = get_object_or_404(
            posts,
            id=post_id,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related('author').filter(post=post)

    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница постов категории"""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = get_posts_with_comments(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    )

    page_obj = get_paginated_page(request, posts)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, "blog/category.html", context)


def profile(request, username):
    """Отображение страницы пользователя"""
    profile_user = get_object_or_404(User, username=username)

    # Определяем, какие посты показывать
    if request.user != profile_user:
        # Для чужих профилей показываем только опубликованные посты
        posts = get_posts_with_comments(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            author=profile_user
        )
    else:
        # Для своего профиля показываем все посты
        posts = get_posts_with_comments(author=profile_user)

    page_obj = get_paginated_page(request, posts)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
        'is_owner': request.user == profile_user
    }
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    """Создание публикации"""
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user

        if not post.pub_date:
            post.pub_date = timezone.now()
        elif post.pub_date > timezone.now():
            post.pub_date = timezone.now()

        post.save()
        return redirect('blog:profile', username=request.user.username)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    """Редактирование публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """Удаление публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария к публикации"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    context = {
        'comment': comment,
        'form': form
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария к публикации"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)

    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def edit_profile(request):
    """Редактирование страницы пользователя"""
    form = UserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)

    context = {'form': form}
    return render(request, 'blog/user.html', context)
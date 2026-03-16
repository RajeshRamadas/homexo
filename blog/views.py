"""
blog/views.py
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Category


def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    paginator = Paginator(posts, 9)
    posts = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()
    return render(request, 'blog/list.html', {'posts': posts, 'categories': categories})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    Post.objects.filter(pk=post.pk).update(views_count=post.views_count + 1)
    related = Post.objects.filter(
        status='published', category=post.category
    ).exclude(pk=post.pk)[:3]
    return render(request, 'blog/detail.html', {'post': post, 'related': related})

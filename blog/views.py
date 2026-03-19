"""
blog/views.py
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Category


def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    category_slug = request.GET.get('category', '').strip()
    query = request.GET.get('q', '').strip()
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if query:
        posts = posts.filter(title__icontains=query)
    paginator = Paginator(posts, 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()
    popular_posts = Post.objects.filter(status='published').select_related('category').order_by('-views_count')[:4]
    return render(request, 'blog/list.html', {
        'posts': page_obj,
        'categories': categories,
        'popular_posts': popular_posts,
        'category_slug': category_slug,
        'query': query,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    Post.objects.filter(pk=post.pk).update(views_count=post.views_count + 1)
    related = Post.objects.filter(
        status='published', category=post.category
    ).exclude(pk=post.pk).select_related('category')[:3]
    prev_post = None
    next_post = None
    if post.published_at:
        prev_post = Post.objects.filter(
            status='published', published_at__lt=post.published_at
        ).order_by('-published_at').first()
        next_post = Post.objects.filter(
            status='published', published_at__gt=post.published_at
        ).order_by('published_at').first()
    return render(request, 'blog/detail.html', {
        'post': post,
        'related': related,
        'prev_post': prev_post,
        'next_post': next_post,
    })

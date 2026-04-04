"""
blog/views.py
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Post, Category
from .forms import PostEditorForm


def post_list(request):
    posts = Post.objects.filter(status='published').select_related('author').prefetch_related('categories')
    category_slug = request.GET.get('category', '').strip()
    query = request.GET.get('q', '').strip()
    if category_slug:
        posts = posts.filter(categories__slug=category_slug).distinct()
    if query:
        posts = posts.filter(title__icontains=query)
    paginator = Paginator(posts, 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()
    popular_posts = Post.objects.filter(status='published').prefetch_related('categories').order_by('-views_count')[:4]
    return render(request, 'blog/list.html', {
        'posts': page_obj,
        'categories': categories,
        'popular_posts': popular_posts,
        'category_slug': category_slug,
        'query': query,
    })


@staff_member_required
def post_create(request):
    if request.method == 'POST':
        form = PostEditorForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == Post.Status.PUBLISHED and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            form.save_m2m()
            if post.status == Post.Status.PUBLISHED:
                return redirect('blog:detail', slug=post.slug)
            return redirect('blog:edit', slug=post.slug)
    else:
        form = PostEditorForm()
    return render(request, 'blog/editor.html', {
        'form': form,
        'categories': Category.objects.all(),
    })


@staff_member_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        form = PostEditorForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.status == Post.Status.PUBLISHED and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            form.save_m2m()
            if post.status == Post.Status.PUBLISHED:
                return redirect('blog:detail', slug=post.slug)
            return redirect('blog:edit', slug=post.slug)
    else:
        form = PostEditorForm(instance=post)
    return render(request, 'blog/editor.html', {
        'form': form,
        'post': post,
        'categories': Category.objects.all(),
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    Post.objects.filter(pk=post.pk).update(views_count=post.views_count + 1)
    related = Post.objects.filter(
        status='published', categories__in=post.categories.all()
    ).exclude(pk=post.pk).prefetch_related('categories').distinct()[:3]
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

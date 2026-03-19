"""
blog/models.py
News, market reports, and blog posts shown in the news carousel.
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    color = models.CharField(max_length=20, default='#4A90C4',
                             help_text='Hex color for tag badge')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Draft'
        PUBLISHED = 'published', 'Published'

    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, related_name='blog_posts')
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='posts')
    title       = models.CharField(max_length=220)
    slug        = models.SlugField(max_length=240, unique=True, blank=True)
    excerpt     = models.TextField(max_length=300, blank=True)
    body        = models.TextField()
    cover_image    = models.ImageField(upload_to='blog/covers/', blank=True, null=True)
    key_takeaways  = models.TextField(
        blank=True,
        help_text='One takeaway per line. Displayed as a bullet list at the start of the article.'
    )
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0, editable=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        words = len(self.body.split())
        return max(1, round(words / 200))

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug, n = base, 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

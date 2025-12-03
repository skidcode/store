from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    published_date = models.DateField(null=True, blank=True)
    cover_image = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

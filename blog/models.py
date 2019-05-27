from django.db import models

from time import time


def gen_slug():
    return str(int(time()))

class Post(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_pub']

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        self.slug = gen_slug()
        super().save(*args, **kwargs)

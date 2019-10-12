from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from time import time


class Post(models.Model):
    title = models.CharField(max_length=200, db_index=True, verbose_name=_("Title"))
    body = models.TextField(blank=True, db_index=False, verbose_name=_("Body"))
    date_pub = models.DateTimeField(auto_now_add=True, verbose_name=_("Date pub."))

    class Meta:
        ordering = ['-date_pub']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail_url', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('post_update_url', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('post_delete_url', kwargs={'pk': self.pk})

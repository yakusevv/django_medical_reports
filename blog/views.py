from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Post


@login_required
def news_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    is_paginated = page.has_other_pages()

    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    context = {
        'page_object': page,
        'is_paginated': is_paginated,
        'prev_url': prev_url,
        'next_url': next_url
    }

    return render(request, 'blog/index.html', context)


class PostDetail(View):
    model = Post
    template = 'blog/post_detail.html'

    def get(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        return render(request, self.template, context={
                                                self.model.__name__.lower(): obj,
                                                'admin_object': obj,
                                                })


class PostCreate(PermissionRequiredMixin, View):
    model_form = PostForm
    template = 'blog/post_create_form.html'
    permission_required = 'blog.can_create'
    raise_exception = True

    def get(self, request):
        form = self.model_form()
        return render(request, self.template, context={'form': form})

    def post(self, request):
        bound_form = self.model_form(request.POST)
        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form': bound_form})


class PostUpdate(PermissionRequiredMixin, View):
    model = Post
    model_form = PostForm
    template = 'blog/post_update_form.html'
    permission_required = 'blog.can_update'
    raise_exception = True

    def get(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        bound_form = self.model_form(instance=obj)
        return render(request, self.template,
                      context={'form': bound_form,
                               self.model.__name__.lower(): obj
                               })

    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        bound_form = self.model_form(request.POST, instance=obj)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)
        return render(request, self.template,
                      context={'form': bound_form,
                               self.model.__name__.lower(): obj
                               })


class PostDelete(PermissionRequiredMixin, View):
    model = Post
    template = 'blog/post_delete_form.html'
    redirect_url = 'posts_list_url'
    permission_required = 'blog.can_delete'
    raise_exception = True

    def get(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        return render(request, self.template, context={
                                                self.model.__name__.lower(): obj
                                                })
    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        obj.delete()
        return redirect(reverse(self.redirect_url))

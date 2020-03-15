from django.shortcuts import render
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View, ListView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Post


class PostList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super(PostList, self).get_context_data()
        context['news_link_active'] = "active"
        return context


class PostDetail(LoginRequiredMixin, View):
    model = Post
    template = 'blog/post_detail.html'

    def get(self, request, pk):
        obj = get_object_or_404(self.model, pk=pk)
        return render(request, self.template, context={
                                                'post': obj,
                                                'admin_obj': obj,
                                                'news_link_active': "active"
                                                })


class PostCreate(PermissionRequiredMixin, View):
    model_form = PostForm
    template = 'blog/post_create_form.html'
    permission_required = 'blog.create_post'

    def get(self, request):
        form = self.model_form()
        return render(request, self.template, context={
                                                'form': form,
                                                'news_link_active': "active"
                                                })

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
    permission_required = 'blog.change_post'

    def get(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        bound_form = self.model_form(instance=obj)
        return render(request, self.template,
                      context={'form': bound_form,
                               'admin_obj': obj,
                               self.model.__name__.lower(): obj,
                               'news_link_active': "active"
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
    permission_required = 'blog.delete_post'

    def get(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        return render(request, self.template, context={
                                                self.model.__name__.lower(): obj,
                                                'news_link_active': "active"
                                                })

    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        obj.delete()
        return redirect(reverse(self.redirect_url))

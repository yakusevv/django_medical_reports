from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404

from .models import Profile

class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'profiles/profile_detail.html'
    model = Profile

    def get(self, request, pk):
        if request.user.profile.pk == pk or request.user.is_staff:
            profile = get_object_or_404(self.model, pk=pk)
            return render(request, self.template_name, context={ 'profile': profile,
                                                                 'profile_link_active': "active"})
        else:
            raise Http404

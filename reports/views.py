from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Patient


class ReportsListView(ListView):
    pass


class PatientDetailView(DetailView):
    model = Patient
    template_name = 'reports/patient_detail.html'

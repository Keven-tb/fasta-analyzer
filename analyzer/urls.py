from django.urls import path

from . import views

urlpatterns = [
    path('', views.upload_fasta, name='upload_fasta'),
    path('sequencias/', views.listar_sequencias, name='listar_sequencias'),
]

from django.urls import path
from .views import (
    DocumentListView,
    DocumentDetailView,
    DocumentDownloadView,
    DocumentUploadView
)

urlpatterns = [
    path('', DocumentListView.as_view(), name='document-list-create'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('<int:pk>/download/', DocumentDownloadView.as_view(), name='document-download'),
]

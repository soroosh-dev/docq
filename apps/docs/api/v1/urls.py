from django.urls import path
from .views import (
    DocumentListView,
    DocumentDetailView,
    DocumentDownloadView,
    DocumentUploadView,
    UserSearchView,
    DocumentPermissionView,
    DocumentQueryView,
    DocumentQueryWithResponseView
)

urlpatterns = [
    path('', DocumentListView.as_view(), name='document-list-create'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('<int:pk>/download/', DocumentDownloadView.as_view(), name='document-download'),
    path('users/search/', UserSearchView.as_view(), name='user-search'),
    path('<int:document_id>/permissions/', DocumentPermissionView.as_view(), name='document-permissions'),
    path('query/', DocumentQueryView.as_view(), name='document-query'),
    path('query-with-response/', DocumentQueryWithResponseView.as_view(), name='document-query-with-response'),
]

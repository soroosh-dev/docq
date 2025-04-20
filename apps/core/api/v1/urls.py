from django.urls import path, include

urlpatterns = [
    path('user/', include(('apps.knockknock.urls', 'knockknock'))),
    path('docs/', include(('apps.docs.api.v1.urls', 'docs'))),
]
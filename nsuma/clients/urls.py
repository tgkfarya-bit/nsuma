from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import logout_view,login_view,register_view,activation_view

app_name = "clients"

urlpatterns = [
    path("",login_view,name='login'),
    path("logout/",logout_view,name='logout'),
    path("register/",register_view,name='register'),
    path("activation/",activation_view,name='activation'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
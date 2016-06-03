from django.conf.urls import url
from researcher import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^get_researchers/$', views.get_researchers, name='get_researchers'),
]

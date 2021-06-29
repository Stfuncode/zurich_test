from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index', views.indexView, name="home"),
    path('dashboard', views.dashboardView, name="dashboard"),
    path('', LoginView.as_view(), {'template_name': 'registration/login.html'}, name="login"),
    path('register', views.register, name="register" ),
    path('homepage', views.homepage, name="homepage" ),
    path('nominationform/<str:pk>', views.nominationform, name='nominationform'),
    path('selfservice/<str:pk>', views.selfservice, name='selfservice'),
    path('msvr/<str:pk>', views.msvr, name='msvr'),
    path('request_change', views.request_change, name="request_change" ),
    path('logout/', views.logout, name='logout'),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]

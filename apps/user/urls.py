"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from apps.user.views import RegisterView, ActiveView, LoginView
from apps.user import views

urlpatterns = [
    # url(r'^register$', views.register, name='register'),    # 注册
    # url(r'^register_handle$', views.register_handle, name='register_handle'),   # 注册处理
    url(r'^register$', RegisterView.as_view(), name='register'),    # 注册
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),     # 激活
    url('^login$', LoginView.as_view(), name='login'),  # 登录
]

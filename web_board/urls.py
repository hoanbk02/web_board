"""web_board URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from boards import views
from accounts import views as acc_views

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),

    url(r'^signup/$', acc_views.signup, name='signup'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            subject_template_name='password_reset_subject.txt',
            email_template_name='password_reset_email.html'
        ), name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),

    url(r'^settings/password/$',
        auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'),
    url(r'^settings/password/done/$',
        auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),
    url(r'^settings/account/$', acc_views.UserUpdateView.as_view(), name='my_account'),

    url(r'^$', views.BoardListView.as_view(), name='home'),
    url(r'^board/(?P<pk>\d+)/$', views.TopicListView.as_view(), name='board_topics'),
    url(r'^board/(?P<pk>\d+)/new/$', views.new_topic, name='new_topic'),
    url(r'^board/(?P<pk>\d+)/topic/(?P<topic_pk>\d+)/$', views.PostListView.as_view(), name='topic_post'),
    url(r'^board/(?P<pk>\d+)/topic/(?P<topic_pk>\d+)/reply/$', views.ReplyPostView.as_view(), name='reply_post'),
    url(r'^board/(?P<pk>\d+)/topic/(?P<topic_pk>\d+)/post/(?P<post_pk>\d+)/edit/$',
        views.PostUpdateView.as_view(),
        name='edit_post'),
]

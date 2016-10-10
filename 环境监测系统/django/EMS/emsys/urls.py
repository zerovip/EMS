from django.conf.urls import url
from .import views

#url(r'^view/(?P<article_id>[0-9]+)/$',views.view,name='view'),

urlpatterns=[
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

    url(r'^dev/add/$', views.dev_add, name='dev_add'),
    url(r'^dev/edit/(?P<id>[0-9]+)/$', views.dev_edit, name='dev_edit'),

    url(r'^usergroup/add/$', views.usgp_add, name='usgp_add'),
    url(r'^usergroup/edit/(?P<id>[0-9]+)/$', views.usgp_edit, name='usgp_edit'),

    url(r'^user/add/(?P<id>[0-9]+)/$', views.user_add, name='user_add'),
    url(r'^user/edit/(?P<id>[0-9]+)/$', views.user_edit, name='user_edit'),
    url(r'user/self/$', views.self, name='self'),

    url(r'^data/history/$', views.data_history, name='data_history'),
    url(r'^data/warning/$', views.data_warning, name='data_warning'),

#    url(r'^api/$',views.api,name='api'),
]

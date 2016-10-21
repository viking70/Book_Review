from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^review$', views.review, name='review'),
    url(r'^add$', views.add, name='add'),
    url(r'^add1$', views.add1),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^book/(?P<bid>[0-9]+)$', views.book, name='book'),
    url(r'^user/(?P<uid>[0-9]+)$', views.user, name='user'),
    url(r'^delete/(?P<rid>[0-9]+)$', views.delete, name='delete')
    # url(r'^remove/(?P<cid>[0-9])$', views.remove, name='remove'),
    # url(r'^remove/delete$', views.delete), # Why use remove/delete instead of delete?
]
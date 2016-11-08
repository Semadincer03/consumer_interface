from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .import views


urlpatterns = [
    url(r'^$', auth_views.login, {'template_name': 'login.html'},
        name='login'),
    url(r'^home/$', views.home),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'},
        name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'},
        name='logout'),
    url(r'^search/$', views.search, name='search'),
    url(r'^results/$', views.results, name='results'),
    url(r'^book/', views.provision, name='provision'),
    url(r'^bookings/', views.bookings, name='bookings'),
    url(r'^provision/(?P<product_code>[\w-]+)/$', views.provision,
        name='provision'),
    url(r'^availability/(?P<hotel_code>[\w-]+)/$', views.availability,
        name='availability'),
]

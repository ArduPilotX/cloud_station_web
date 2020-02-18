from django.urls import path 
from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^connect/(?P<connect_address>[^/]+)/$', views.connect_vehicle, name='connect-vehicle'),
    url('disconnect/', views.disconnect_vehicle, name='disconnect-vehicle'),
    url(r'control/setmode/(?P<droneid>[^/]+)/(?P<mode>[^/]+)/$', views.set_mode, name='set-mode')
    # url(r'control/setwaypoint/(?P<droneid>[^/]+)/(?P<waypoint>[^/]+)/$', views.set_waypoint, name='set-waypoint')
]
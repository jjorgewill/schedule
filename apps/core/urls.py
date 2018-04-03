from django.conf.urls import url

from apps.core import views

urlpatterns = [
    url(r'^$', views.Dashboard.as_view(), name='view_dashboard'),
    url(r'^router/$', views.RouterView.as_view(), name='router'),
    url(r'^hours/$', views.HoursView.as_view(), name='view_hours'),
    url(r'^hours/create/$', views.HoursCreateView.as_view(), name='create_hours'),
    url(r'^holiday/$', views.HolidaysView.as_view(), name='view_holidays'),
    url(r'^holiday/create/$', views.HolidaysCreateView.as_view(), name='create_holidays'),
    url(r'^profiles/$', views.ProfilesView.as_view(), name='view_profiles'),
    url(r'^profiles/create/$', views.ProfilesCreateView.as_view(), name='create_profiles'),
    url(r'^profiles/update/(?P<pk>\d+)/$', views.ProfilesUpdateView.as_view(), name='update_profiles'),
    url(r'^professions/$', views.ProfessionsView.as_view(), name='view_professions'),
    url(r'^professions/create/$', views.ProfessionsCreateView.as_view(), name='create_professions'),
    url(r'^turns/$', views.TurnsView.as_view(), name='view_turns'),
    url(r'^turns/create/$', views.TurnsCreateView.as_view(), name='create_turns'),
    url(r'^calendar/$', views.CalendarView.as_view(), name='create_calendar'),
    url(r'^get_turns/$', views.GetTurnsView.as_view(), name='get_turns'),
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("hotlines/", views.hotlines_view, name="hotlines"),
    path("what-to-do/", views.what_to_do_view, name="what_to_do"),
    path("centers/", views.centers_map_view, name="centers_map"),
    path("referral-network/", views.referral_network_join_view, name="referral_network_join"),
    path("dispatch-centers/", views.dispatch_centers_subquery_view, name="dispatch_centers_subquery"),
]

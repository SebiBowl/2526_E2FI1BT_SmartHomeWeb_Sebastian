from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("showtemps/", views.display_temps),
    path("showhumid/", views.display_humids), #Neu
    path("showpress/", views.display_press), #Neu
    path("sensors/", views.display_sensors),
    path("showtemps/<str:temp_id>/", views.tempdetails, name="temp_detail"),
    path("showpress/<str:temp_id>/", views.tempdetails, name="press_detail"),
    path("sensors/editsensor/<str:sensor_id>/", views.edit_sensor_details),
    path("sensors/sensor_new/", views.new_sensor),
]

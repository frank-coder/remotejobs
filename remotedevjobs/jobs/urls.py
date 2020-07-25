from django.urls import path,include
from . import views

app_name = "jobs"

urlpatterns = [
	path('',views.homepage,name='homepage'),
	
]
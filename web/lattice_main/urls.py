from django.urls import path
from . import views

urlpatterns = [
    path('',views.upload_circuit, name='lattice_main-uploadcircuit'),
    path('lattice_view/',views.view_compiled,name='lattice_main-latticeview'),
    path('contact/',views.contact,name='lattice_main-contact'),
]
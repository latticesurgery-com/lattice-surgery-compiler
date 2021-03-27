from django.urls import path
from . import views

urlpatterns = [
    path('',views.upload_circuit, name='lattice_main-uploadcircuit'),
    path('lattice_view/',views.view_compiled,name='lattice_main-latticeview'),
    path('render_file/',views.render_to_file,name='lattice_main-render-to-file'),
]
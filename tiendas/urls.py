# urls.py

from django.urls import path
from .views import BuscarProductosView

urlpatterns = [
    # La vista GET de la raíz mostrará el formulario de búsqueda inicial
    path('', BuscarProductosView.as_view(), name='home'), 
    
    # La acción POST del formulario apuntará aquí
    path('buscar/', BuscarProductosView.as_view(), name='buscar'),
]
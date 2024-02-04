from django.urls import path
from ems.forms import ReturnSelectorFormSet, ExchangeSelectorFormSet
from ems.views import EmsWizard

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('contact/', EmsWizard.as_view([ReturnSelectorFormSet,ExchangeSelectorFormSet])),
]
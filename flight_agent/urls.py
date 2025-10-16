from django.urls import path
from .views import FlightSearchView, ChatHistoryView, SearchHistoryView

urlpatterns = [
    path('flight-search/', FlightSearchView.as_view(), name='flight-search'),
    path('chat-history/', ChatHistoryView.as_view(), name='chat-history'),
    path('search-history/', SearchHistoryView.as_view(), name='search-history'),
]

from django.urls import path
from .views import LastPlayed, PlayedStats, AccountInfo

urlpatterns = [
    path('last-played/', LastPlayed.as_view(), name='last-played'),
    path('top-stats/', PlayedStats.as_view(), name='top-stats'),
    path('account-info/', AccountInfo.as_view(), name='account-info'),

]
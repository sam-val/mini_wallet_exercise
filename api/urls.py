from django.urls import path, re_path
from . import views


app_name = "api"
urlpatterns = [
    re_path(r'^wallet/?$', views.wallet, name='access_wallet'),
    re_path(r'^init/?$', views.init, name='init_wallet'),
    re_path(r'^wallet/withdrawals/?$', views.withdrawals, name='withdrawals'),
    re_path(r'^wallet/deposits/?$', views.deposits, name='deposits'),
]

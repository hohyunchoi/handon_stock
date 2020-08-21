"""config URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from stock import views
urlpatterns = [
    path('', views.login, name="login"),
    path('login', views.login),
    path('home', views.home, name="home"),
    path("logout", views.logout, name="logout"),
    path("account_ajax", views.account),
    path("stockchart",views.stockchart),
    path("stockchart_ajax",views.stockchartajax),
    path("page_ajax",views.paging),
    path("stockdetail",views.stockdetail),
    path("stocktoday",views.today),
    path("stockorder",views.order),
    path("hogatable",views.hogatable),
    path("buyorder",views.buyorder),
    path("sellorder",views.sellorder),
    path("stockwallet",views.stockwallet),
    path("stockwallet_ajax",views.stockwallet_ajax),
    path("createaccount",views.createaccount,name="createaccount")
]
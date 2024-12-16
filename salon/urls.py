"""
URL configuration for salon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HealthCheckView(APIView):
    """
    Simple health check endpoint to ensure the app is running properly.
    """
    def get(self, request, *args, **kwargs):
        # You can add additional logic here, like checking database connections, etc.
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HealthCheckView.as_view(), name='health_check'),
    path('auth/',include('accounts.urls')),
    path('service/',include('service.urls')),

]

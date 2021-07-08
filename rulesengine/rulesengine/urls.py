"""rulesengine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path

from rules import views

# Useful Admin UI customization info:
# https://www.webforefront.com/django/admincustomlayout.html
admin.site.site_header = 'Rules Engine'
admin.site.site_title = 'Rules Engine'
admin.site.site_url = None
admin.site.index_title = 'Rules Engine Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rules', views.RulesView.as_view()),
    path('rules/tree/<path:surt_string>', views.rules_for_surt),
    path('rules/for-request', views.rules_for_request),
    path('rule/<int:pk>', views.RuleView.as_view()),
]

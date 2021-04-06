"""askme_kasupovich URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='new_questions'),
    path('hot/', views.hot_questions, name='hot_questions'),
    path('ask/', views.new_question, name='new_question'),
    path('question/<int:pk>/', views.one_question, name='one_question'),
    path('tag/<slug:name>/', views.questions_by_tag, name='questions_by_tag'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('personal_page/', views.personal_page, name='personal_page'),
]

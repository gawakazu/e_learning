from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import MainView,TaskView,MaterialView,ExamView,ResultView,LoginView,LogoutView,KanriView,InformationView,IndexView#,RetaskView

urlpatterns =[
    path('',LoginView.as_view(),name='login'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
    path('main/',MainView.as_view(),name='main'),
    path('task/<int:pk>/',TaskView.as_view(),name='task'),
    path('task/<str:material>/',TaskView.as_view(),name='task'),
    path('text/<str:i>/',MaterialView.as_view(),name='material'),
    path('exam/<str:task>/',ExamView.as_view(),name='exam'),
    path('result/<str:task>/',ResultView.as_view(),name='result'),
    path('kanri/',KanriView.as_view(),name='kanri'),
    path('information/',InformationView.as_view(),name='information'),
    path('index/<str:select>/',IndexView.as_view(),name='index'),
] +static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


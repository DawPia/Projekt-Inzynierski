from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('diety/', views.diet_list_view, name='diet_list'),
    path('rejestracja/', views.register_view, name='register'),
    path('logowanie/', views.login_view, name='login'),
    path('wylogowanie/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('kalkulator/', views.calculator_view, name='calculator'),
    path('diety/<int:pk>/', views.diet_detail_view, name='diet_detail'),
    path('dania/', views.dish_list_view, name='dish_list'),  path('dish/<int:pk>/favorite/', views.toggle_dish_favorite, name='toggle_dish_favorite'),
    path('dania/<int:pk>/', views.dish_detail_view, name='dish_detail'),
    path('diet/<int:pk>/favorite/', views.toggle_diet_favorite, name='toggle_diet_favorite'),
    path('dish/<int:pk>/favorite/', views.toggle_dish_favorite, name='toggle_dish_favorite'),
]
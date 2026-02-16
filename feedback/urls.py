from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_list, name='feedback_list'),
    path('delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
    path('edit/<int:feedback_id>/', views.edit_feedback, name='edit_feedback'),

]

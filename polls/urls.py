from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/<int:user_id>/vote/', views.vote_unsafe, name='vote_unsafe'),   # FLAW 1
    path('<int:question_id>/vote/', views.vote_safe, name='vote_safe'),
    path('<int:pk>/already_voted/', views.AlreadyVotedView.as_view(), name='already_voted'),
    path('add_message/', views.add_message, name='add_message'),
    path('forgot_my_password/', views.forgot_my_password, name='forgot_my_password'),
    path('security_question/', views.security_question, name='security_question'),
    path('change_password/', views.change_password, name='change_password'),
]

from django.urls import path
from .views import list_view, index_view, create_view, delete_view, detail_view, update_view, triagem_view, dashboard_view, registro_view, perfil_view, mudar_status_view, feedback_view, lista_feedback_view, gestao_view, ver_perfil_usuario_view, delete_user_view, partial_patient_list_view
from django.contrib.auth import views as auth_views

app_name = 'hosp'
urlpatterns = [
    path('home/', index_view, name='index'),
    path('criar/', create_view, name='criar'),
    path('listar/', list_view, name='listar'),
    path('detail/<int:pk>', detail_view, name='mostrar'),
    path('atualizar/<int:pk>', update_view, name='atualizar'),
    path('deletar/<int:pk>', delete_view, name='deletar'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('triagem/', triagem_view, name='triagem'),

    path('registro/', registro_view, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='site/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='hosp:login'), name='logout'),
    path('perfil/', perfil_view, name='perfil'),
    path('paciente/<int:pk>/mudar-status/', mudar_status_view, name='mudar_status'),

    path('paciente/<int:pk>/feedback/', feedback_view, name='dar_feedback'),
    path('feedback/lista/', lista_feedback_view, name='lista_feedback'),
    path('gestao/', gestao_view, name='painel_gestao'),
    path('gestao/ver-perfil/<int:pk>/', ver_perfil_usuario_view, name='ver_perfil_usuario'),
    path('gestao/remover-usuario/<int:pk>/', delete_user_view, name='remover_usuario'),

    path('partials/patient-list/', partial_patient_list_view, name='partial_patient_list'),
]

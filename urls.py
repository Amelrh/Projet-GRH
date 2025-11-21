"""
URL configuration for Gestion_Rh project.

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
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from GestioRH.views import (
    EventCreateView,
    EventDayArchiveView,
    EventDeleteView,
    EventMonthArchiveView,
    EventYearArchiveView,
    add_favoris,
    analyse_employes,
    archive_contrat_delete,
    archive_contrat_detail,
    archive_contrat_list,
    calendar_view,
    candidats_list,
    candidature_create,
    candidature_delete,
    changer_statut_candidature,
    confirm_registration,
    contact,
    contact_success,
    contrat_archive,
    contrat_detail,
    delete_message,
    delete_notification,
    demander_avance,
    edit_event,
    entretien_delete,
    entretien_update,
    event_list,
    favoris_list,
    fiche_paie_create,
    fiche_paie_delete,
    fiche_paie_detail,
    fiche_paie_list,
    fiche_paie_update,
    inbox,
    legal_mentions,
    liste_absences,
    liste_cvs,
    liste_retards,
    mark_as_read,
    marquer_absence,
    marquer_retard,
    notifications,
    remove_favoris,
    send_message,
    solde_conge_create,
    solde_conge_delete,
    solde_conge_list,
    solde_conge_update,
    user_login,
    register,
    demander_conge,
    entretien_create,
    entretien_list,
    home,
    mise_a_jour_statut_candidature,
    offre_emploi_create,
    offre_emploi_delete,
    offre_emploi_list,
    offre_emploi_update,
    prime_create,
    prime_delete,
    prime_list,
    prime_update,
    dashboard,  
    employe_list, employe_create, employe_update, employe_delete,
    service_list, service_create, service_update, service_delete,
    conge_list, conge_create, conge_update, conge_delete,
    contrat_list, contrat_create, contrat_update, contrat_delete,
    salaire_list, salaire_create, salaire_update, salaire_delete,
    recrutement_list, recrutement_create, recrutement_update, recrutement_delete,
    evaluation_list, evaluation_create, evaluation_update, evaluation_delete,
    evaluation_report, evaluation_detail,  
    fiche_employe_list, fiche_employe_create, fiche_employe_update, fiche_employe_delete,
    type_conge_list, type_conge_create, type_conge_update, type_conge_delete,
    type_contrat_list, type_contrat_create, type_contrat_update, type_contrat_delete,
    user_logout,
    view_message,
     
)


urlpatterns = [

    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'), 
    path('accounts/login/', lambda request: redirect(reverse_lazy('login'))),   
    path('confirm_registration/', confirm_registration, name='confirm_registration'),
    path('dashboard/', dashboard, name='dashboard'),
    path('mentions-legales/', legal_mentions, name='legal_mentions'),  
    path('contact/', contact, name='contact'),  
    path('contact/success/', contact_success, name='contact_success'),  

    # URLs pour les Favoris
    path('favoris/', favoris_list, name='favoris_list'),
    path('favoris/add/<int:fonctionnalite_id>/', add_favoris, name='favoris_add'),
    path('favoris/remove/<int:fonctionnalite_id>/', remove_favoris, name='favoris_remove'),

    # URLs pour les Employés
    path('employes/', employe_list, name='employe_list'),
    path('employes/ajouter/', employe_create, name='employe_create'),
    path('employes/modifier/<int:pk>/', employe_update, name='employe_update'),
    path('employes/supprimer/<int:pk>/', employe_delete, name='employe_delete'),

    # URLs pour les Services
    path('services/', service_list, name='service_list'),
    path('services/ajouter/', service_create, name='service_create'),
    path('services/modifier/<int:pk>/', service_update, name='service_update'),
    path('services/supprimer/<int:pk>/', service_delete, name='service_delete'),

    # URLs pour les Congés
    path('conges/', conge_list, name='conge_list'),
    path('conges/ajouter/', conge_create, name='conge_create'),
    path('conges/modifier/<int:pk>/', conge_update, name='conge_update'),
    path('conges/supprimer/<int:pk>/', conge_delete, name='conge_delete'),


# URLs pour les Contrats
    path('contrats/', contrat_list, name='contrat_list'),
    path('contrats/ajouter/', contrat_create, name='contrat_create'),
    path('contrats/modifier/<int:pk>/', contrat_update, name='contrat_update'),
    path('contrats/supprimer/<int:pk>/', contrat_delete, name='contrat_delete'),
    path('contrats/<int:pk>/', contrat_detail, name='contrat_detail'),

# URLs pour Archives contrats  
    path('archives/', archive_contrat_list, name='archive_contrat_list'),
    path('archives/<int:pk>/', archive_contrat_detail, name='archive_contrat_detail'),
    path('archives/<int:pk>/delete/', archive_contrat_delete, name='archive_contrat_delete'), 
    path('contrats/<int:pk>/archive/', contrat_archive, name='contrat_archive'),
    

    # URLs pour les Salaires
    path('salaires/', salaire_list, name='salaire_list'),
    path('salaires/ajouter/', salaire_create, name='salaire_create'),
    path('salaires/modifier/<int:pk>/', salaire_update , name='salaire_update'),
    path('salaires/supprimer/<int:pk>/', salaire_delete, name='salaire_delete'),

    # URLs pour les Recrutements
    path('recrutements/', recrutement_list, name='recrutement_list'),  
    path('recrutements/ajouter/', recrutement_create, name='recrutement_create'),  
    path('recrutements/modifier/<int:pk>/', recrutement_update, name='recrutement_update'), 
    path('recrutements/supprimer/<int:pk>/', recrutement_delete, name='recrutement_delete'), 

    # URLs pour les Évaluations
    path('evaluations/', evaluation_list, name='evaluation_list'),
    path('evaluations/ajouter/', evaluation_create, name='evaluation_create'),
    path('evaluations/modifier/<int:pk>/', evaluation_update, name='evaluation_update'),
    path('evaluations/supprimer/<int:pk>/', evaluation_delete, name='evaluation_delete'),
    path('evaluations/rapport/', evaluation_report, name='evaluation_report'),
    path('evaluations/detail/<int:pk>/', evaluation_detail, name='evaluation_detail'),

    # URLs pour les Fiches Employés
    path('fiches-employes/', fiche_employe_list, name='fiche_employe_list'),
    path('fiches-employes/ajouter/', fiche_employe_create, name='fiche_employe_create'),
    path('fiches-employes/modifier/<int:pk>/', fiche_employe_update, name='fiche_employe_update'),
    path('fiches-employes/supprimer/<int:pk>/', fiche_employe_delete, name='fiche_employe_delete'),
    path('analyse-employes/', analyse_employes, name='analyse_employes'),

    # URLs pour les Types de Congés
    path('types-conge/', type_conge_list, name='type_conge_list'),
    path('types-conge/ajouter/', type_conge_create, name='type_conge_create'),
    path('types-conge/modifier/<int:pk>/', type_conge_update, name='type_conge_update'),
    path('types-conge/supprimer/<int:pk>/', type_conge_delete, name='type_conge_delete'),

    # URLs pour les soldes de Congés
    path('soldes/', solde_conge_list, name='solde_conge_list'),  
    path('soldes/ajouter/', solde_conge_create, name='solde_conge_create'),  
    path('soldes/modifier/<int:pk>/', solde_conge_update, name='solde_conge_update'), 
    path('soldes/supprimer/<int:pk>/', solde_conge_delete, name='solde_conge_delete'), 

    # URLs pour les Types de Contrats
    path('types-contrat/', type_contrat_list, name='type_contrat_list'),
    path('types-contrat/ajouter/', type_contrat_create, name='type_contrat_create'),
    path('types-contrat/modifier/<int:pk>/', type_contrat_update, name='type_contrat_update'),
    path('types-contrat/supprimer/<int:pk>/', type_contrat_delete, name='type_contrat_delete'), 

    # URLs pour les Demandes d'Avance et de Congé
    path('demander-avance/', demander_avance, name='demander_avance'),
    path('demander-conge/', demander_conge, name='demander_conge'),

    # URL pour la Fiche de Paie
    path('fiche-paie/', fiche_paie_list, name='fiche_paie_list'),  
    path('fiche-paie/ajouter/', fiche_paie_create, name='fiche_paie_create'),  
    path('fiche-paie/<int:pk>/modifier/', fiche_paie_update, name='fiche_paie_update'),  
    path('fiche-paie/<int:pk>/supprimer/', fiche_paie_delete, name='fiche_paie_delete'),  
    path('fiche-paie/<int:pk>/', fiche_paie_detail, name='fiche_paie_detail'),  
    path('avance/create/', demander_avance, name='avance_create'),    

    # URLs pour la Gestion des Primes
    path('primes/', prime_list, name='prime_list'),
    path('primes/ajouter/', prime_create, name='prime_create'),
    path('primes/modifier/<int:pk>/', prime_update, name='prime_update'),
    path('primes/supprimer/<int:pk>/', prime_delete, name='prime_delete'),

    # URLs pour les offres d'emploi
    path('offres/', offre_emploi_list, name='offre_emploi_list'),
    path('offres/ajouter/', offre_emploi_create, name='offre_emploi_create'),
    path('offres/<int:pk>/modifier/', offre_emploi_update, name='offre_emploi_update'),
    path('offres/<int:pk>/supprimer/', offre_emploi_delete, name='offre_emploi_delete'),
    path('candidature/<int:offre_id>/', candidature_create, name='candidature_create'),  

    # URLs pour les candidats 
    path('candidats/', candidats_list, name='candidats_list'),
    path('offres/<int:offre_id>/candidature/', candidature_create, name='candidature_create'),
    path('candidature/create/<int:offre_id>/', candidature_create, name='candidature_create'),
    path('candidatures/<int:pk>/ modifier/', mise_a_jour_statut_candidature, name='mise_a_jour_statut_candidature'),
    path('candidats/changer_statut/<int:pk>/', changer_statut_candidature, name='changer_statut_candidature'),
    path('candidats/supprimer/<int:pk>/', candidature_delete, name='candidature_delete'),
    path('cvs/', liste_cvs, name='liste_cvs'),

    # URLs pour les entretiens
    path('entretiens/', entretien_list, name='entretien_list'),
    path('candidature/<int:candidature_id>/entretien/', entretien_create, name='entretien_create'),
    path('entretiens/<int:pk>/modifier/', entretien_update, name='entretien_update'),
    path('entretiens/<int:pk>/supprimer/', entretien_delete, name='entretien_delete'),

    #URLs pour les absences
    path('absences/', liste_absences, name='liste_absences'),
    path('marquer-absence/', marquer_absence, name='marquer_absence'),

    #URLs pour les retards
    path('retards/', liste_retards, name='liste_retards'),
    path('marquer-retard/', marquer_retard, name='marquer_retard'),

    #URLs pour Calendrier
    path('events/add/', EventCreateView.as_view(), name='event_add'),
    path('events/month/<int:year>/<int:month>/', EventMonthArchiveView.as_view(), name='event_month_archive'),
    path('events/year/<int:year>/', EventYearArchiveView.as_view(), name='event_year_archive'),
    path('calendar/', calendar_view, name='calendar_view'),
    path('events/', event_list, name='event_list'),
    path('events/<int:pk>/edit/', edit_event, name='event_edit'),
    path('calendar/<int:year>/<int:month>/', calendar_view, name='calendar_view'),  
    path('event/add/', EventCreateView.as_view(), name='event_add'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('events/day/<int:year>/<int:month>/<int:day>/', EventDayArchiveView.as_view(), name='event_day_archive'),

    #URLS pour Messages
    path('send/', send_message, name='send_message'),
    path('inbox/', inbox, name='inbox'),
    path('view_message/<int:message_id>/', view_message, name='view_message'), 
    path('notifications/', notifications, name='notifications'),
    path('delete/<int:message_id>/', delete_message, name='delete_message'),
    path('notifications/mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
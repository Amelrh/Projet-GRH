import calendar
from datetime import datetime, timedelta 
from datetime import date
from email.message import EmailMessage
from django.forms import ValidationError
from django.utils import timezone
from django.views.generic import CreateView
from django.shortcuts import render
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.contrib.auth import logout , get_user_model
from django.db.models.functions import Cast , Substr  
from django.db.models import IntegerField, Max
import json
import random
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.dates import MonthArchiveView
from django.views.generic.dates import DayArchiveView
from django.views.generic.dates import YearArchiveView
from django.db.models.functions import TruncMonth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User ,Group
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Count
import matplotlib.pyplot as plt
import io
import base64
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from .utils import calculer_salaire, envoyer_notification_candidature, envoyer_notification_entretien
from .models import (
    Absence, ArchiveContrat, AvanceSalaire, Candidature, Employe, Entretien, Favoris, FichePaie, Fonctionnalite, Notification, OffreEmploi, Prime, Profile, Retard, Service, 
    Conge, Contrat, Salaire, Recrutement,  Event, Message,
    Evaluation, FicheEmploye, SoldeConge, TypeConge,ArchiveContrat, TypeContrat,Candidature, OffreEmploi 
)
from .forms import (
     AbsenceForm, CandidatureForm, ContactForm, EntretienForm, EventForm, FichePaieForm, MessageForm, OffreEmploiForm, PrimeForm, RetardForm, SoldeCongeForm, TypeContratForm, UserRegistrationForm, EmployeForm, ServiceForm, 
    CongeForm, ContratForm, SalaireForm, 
    RecrutementForm, EvaluationForm, FicheEmployeForm, 
    TypeCongeForm 
)

from django.contrib.auth.decorators import login_required
from .utils import envoyer_notification_entretien


# Home 
def home(request):
    context = {
        'can_view_calendar': request.user.has_perm('GestioRH.view_calendar'),
        'can_view_employe': request.user.has_perm('GestioRH.view_employe'),
        'can_view_conge': request.user.has_perm('GestioRH.view_conge'),
        'can_view_type_conge': request.user.has_perm('GestioRH.view_type_conge'),
        'can_view_solde_conge': request.user.has_perm('GestioRH.view_solde_conge'),
        'can_view_contrat': request.user.has_perm('GestioRH.view_contrat'),
        'can_view_salaire': request.user.has_perm('GestioRH.view_salaire'),
        'can_view_recrutement': request.user.has_perm('GestioRH.view_recrutement'),
        'can_view_evaluation': request.user.has_perm('GestioRH.view_evaluation'),
        'can_view_fiche_paie': request.user.has_perm('GestioRH.view_fiche_paie'),
        'can_view_prime': request.user.has_perm('GestioRH.view_prime'),
        'can_view_fiche_employe': request.user.has_perm('GestioRH.view_fiche_employe'),
        'can_view_service': request.user.has_perm('GestioRH.view_service'),
        'can_view_type_contrat': request.user.has_perm('GestioRH.view_type_contrat'),
        'can_view_favoris': request.user.has_perm('GestioRH.view_favoris'),
        'can_view_entretien_list': request.user.has_perm('GestioRH.view_entretien_list'),
        'can_view_candidats': request.user.has_perm('GestioRH.view_candidats'),
        'can_view_archive_contrat': request.user.has_perm('GestioRH.view_contrat_archive_list'),
        'can_view_liste_absences': request.user.has_perm('GestioRH.view_liste_absences'), 
        'can_view_liste_retards': request.user.has_perm('GestioRH.view_liste_retards'),  
        'can_view_inbox': request.user.has_perm('GestioRH.view_inbox'),  
        'is_responsable_or_manager': is_responsable_rh(request.user) or is_manager(request.user),
        'is_utilisateur': is_utilisateur(request.user),
    }
    return render(request, 'home.html', context)


def legal_mentions(request):
    return render(request, 'legal_mentions.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)  
        if form.is_valid(): 
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            return redirect('contact_success')  
    else:
        form = ContactForm()  
    
    return render(request, 'contact.html', {'form': form}) 

def contact_success(request):
    return render(request, 'contact_success.html') 
def user_logout(request):
    logout(request)  
    return redirect('home')
@login_required
def ma_vue(request):
    if not request.user.has_perm('app.permission_name'):
        messages.error(request, "Vous n'avez pas la permission d 'accéder à cette page.")
        return redirect('home')

#Fonctions de test pour les rôles
def is_responsable_rh (user):
    return  user.is_superuser or  user.groups.filter(name='Responsables RH').exists() 

def is_manager(user):
    return user.groups.filter(name='Managers').exists()

def is_utilisateur(user):
    return user.groups.filter(name='Utilisateurs').exists()

    

# Inscription
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Générer un code de confirmation
            confirmation_code = random.randint(100000, 999999)

            # Envoyer l'e-mail de confirmation
            subject = "Confirmation de votre inscription"
            message = f"Votre code de confirmation est : {confirmation_code}"
            from_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, from_email, [form.cleaned_data['email']])

            # Stocker le code de confirmation dans la session
            request.session['confirmation_code'] = confirmation_code
            request.session['user_id'] = user.id  

            messages.success(request, "Un e-mail de confirmation a été envoyé. Veuillez vérifier votre boîte de réception.")
            return redirect('confirm_registration')  
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})
#  Vue de confirmation
def confirm_registration(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if code == str(request.session.get('confirmation_code')):
            user_id = request.session.get('user_id')
            user = User.objects.get(id=user_id)
            user.is_active = True  
            user.save()
            messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.")
            return redirect('login')  # Rediriger vers la page de connexion
        else:
            messages.error(request, "Le code de confirmation est incorrect.")
    return render(request, 'confirm_registration.html')
#Vue Login 
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirection en fonction du rôle de l'utilisateur
            if user.is_superuser:
                return redirect('home')  
            elif user.groups.filter(name='Responsables RH').exists():
                return redirect('home')  
            elif user.groups.filter(name='Managers').exists():
                return redirect('home')  
            else:
                return redirect('home')  
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'login.html')

# Fonction pour vérifier si l'utilisateur est un responsable RH
@login_required
@user_passes_test(is_responsable_rh)
def dashboard(request):
    return render(request, 'dashboard.html') 

# Vues pour les Favoris
@login_required
def favoris_list(request):
    favoris = Favoris.objects.filter(user=request.user)
    return render(request, 'favoris_list.html', {'favoris': favoris})
@login_required
def add_favoris(request, fonctionnalite_id):
    if request.method == 'POST':
        fonctionnalite = get_object_or_404(Fonctionnalite, id=fonctionnalite_id)
        favoris, created = Favoris.objects.get_or_create(user=request.user, fonctionnalite=fonctionnalite)
        
        if created:
            return JsonResponse({'success': True, 'message': f"{fonctionnalite.nom} a été ajouté à vos favoris.", 'fonctionnalite_nom': fonctionnalite.nom,'date_ajout': favoris.date_ajout.strftime('%Y-%m-%d %H:%M:%S')})
        else:
            return JsonResponse({'success': False, 'message': f"{fonctionnalite.nom} est déjà dans vos favoris."})
    return JsonResponse({'success': False, 'message': "Méthode non autorisée."})
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Favoris

@login_required
def remove_favoris(request, fonctionnalite_id):
    if request.method == 'POST':
        try:
            favoris = Favoris.objects.get(user=request.user, fonctionnalite_id=fonctionnalite_id)
            favoris.delete()
            return JsonResponse({'success': True, 'message': "Favori supprimé avec succès."})
        except Favoris.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Ce favori n'existe pas."})
    return JsonResponse({'success': False, 'message': "Méthode non autorisée."})



# Vues pour les Employés
@login_required
def employe_list(request):
    # Récupérer tous les employés
    employes = Employe.objects.all()
    return render(request, 'employe_list.html', {'employes': employes})

def generateCodeEmploye():
    max_code = Employe.objects.annotate( numeric_part=Cast(Substr('code', 4), IntegerField()) ).aggregate(max_numeric=Max('numeric_part'))['max_numeric'] 
    max_code += 1
    if max_code is None:
        max_emp_code = "EMP0001"
    else:
        max_emp_code = f"EMP{str(max_code).zfill(4)}"
    return max_emp_code
    

@login_required
@user_passes_test(is_responsable_rh)
def employe_create(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            employe = form.save(commit=False)  
            employe.code = generateCodeEmploye()
            employe.save()  
            print (employe.email)
            user = User.objects.create_user(username=employe.email, password=employe.password)
            group = Group.objects.get(name="Utilisateurs") 
            user.groups.add(group)
            messages.success(request, "Employé ajouté avec succès !")
            return redirect('employe_list')  
    else:
        form = EmployeForm()
    
    return render(request, 'employe_form.html', {'form': form})


@login_required
@user_passes_test(is_responsable_rh)
def employe_update(request, pk):
    employe = get_object_or_404(Employe, pk=pk)

    # Vérifiez si la liste des employés est vide
    if not Employe.objects.exists() and request.user.is_superuser:
        messages.warning(request, "Aucun employé trouvé. Vous pouvez créer un nouvel employé.")
        return redirect('employe_create')

    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employé mis à jour avec succès !')
            return redirect('employe_list')
    else:
        form = EmployeForm(instance=employe)

    return render(request, 'employe_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def employe_delete(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    user = User.objects.get(username=employe.email)
    if request.method == 'POST':
        user.delete()
        employe.delete()
        messages.success(request, 'Employé supprimé avec succès !')
        return redirect('employe_list')
    return render(request, 'employe_confirm_delete.html', {'employe': employe})

@login_required
@user_passes_test(is_responsable_rh)
def analyse_employes(request):
    employe_count = Employe.objects.count()
    
    # Effectifs par type de contrat
    effectifs_par_contrat = Employe.objects.values('type_contrat').annotate(count=Count('id'))

    # Statistiques de diversité
    sexe_count = Employe.objects.values('sexe').annotate(count=Count('id'))  
    age_distribution = {
        'moins_de_30': Employe.objects.filter(date_naissance__gt=timezone.now().year - 30).count(),
        'entre_30_et_50': Employe.objects.filter(date_naissance__lte=timezone.now().year - 30, date_naissance__gt=timezone.now().year - 50).count(),
        'plus_de_50': Employe.objects.filter(date_naissance__lte=timezone.now().year - 50).count(),
    }
    
    # Top performeurs
    top_performeurs = Evaluation.objects.order_by('-score')[:5] 

    context = {
        'employe_count': employe_count,
        'effectifs_par_contrat': effectifs_par_contrat,
        'sexe_count': sexe_count,
        'age_distribution': age_distribution,
        'top_performeurs': top_performeurs,
    }

    return render(request, 'analyse_employes.html', context)

# Vues pour les Services
@login_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})

def generateCodeService(): 
    last_service = Service.objects.last()
    if last_service: 
        numeric_part = int(last_service.code[3:]) 
        new_numeric_part = str(numeric_part + 1).zfill(4) 
        new_code = "SRV" + new_numeric_part 
    else: 
        new_code = "SRV0001" 
    return new_code

def extraire_premiers_caracteres(nom): 
        mots = nom.split() 
        if len(mots) == 1: 
            return nom
        result = ''.join([mot[0] for mot in mots]) 
        return result

@login_required
@user_passes_test(is_responsable_rh)
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.code = generateCodeService()
            service.email_responsable =f"{service.responsable.lower()}@{extraire_premiers_caracteres(service.nom)}.com" 
            service.save()
            messages.success(request, 'Service créé avec succès !')
            return redirect('service_list')
    else:
        form = ServiceForm()
    
    return render(request, 'service_form.html', {'form': form})
@login_required 
@user_passes_test(is_responsable_rh)
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service mis à jour avec succès !')
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'service_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service supprimé avec succès !')
        return redirect('service_list')
    return render(request, 'service_confirm_delete.html', {'service': service})

# Vues pour les Congés
@login_required
def conge_list(request):
    is_responsable_or_manager = request.user.groups.filter(name='Responsables RH').exists() or request.user.groups.filter(name='Managers').exists()

    if is_responsable_or_manager:
        conges = Conge.objects.all()
    else:
        try:
           
            profile = request.user.profile
            employe = profile.employe  
            conges = Conge.objects.filter(employe=employe)
        except Profile.DoesNotExist:
            conges = []  

    return render(request, 'conge_list.html', {'conges': conges, 'is_responsable_or_manager': is_responsable_or_manager})
# Vue pour créer un congé
@login_required 
def conge_create(request):

    if request.method == 'POST':  
        form = CongeForm(request.POST) 
        if form.is_valid():  
            conge =form.save(commit=False)  
            conge.jours_utilises = (conge.date_fin - conge.date_debut + timedelta(days=1)).days
            sc = SoldeConge.objects.get(employe=conge.employe)
            if (sc.solde_restant - conge.jours_utilises) < 0:
                raise ValidationError("Le solde de congé est insuffisant.")
            sc.solde_utilise += conge.jours_utilises
            sc.solde_restant -= conge.jours_utilises
            conge.save()
            sc.save()
            messages.success(request, 'Congé demandé avec succès !')  
            return redirect('conge_list')  
        else:
            messages.error(request, str(form.errors)) 
    else:
        form = CongeForm(user=request.user)  
    return render(request, 'conge_form.html', {'form': form})
# Vue pour mettre à jour un congé
@login_required
@user_passes_test(is_responsable_rh)
def conge_update(request, pk):
    conge = get_object_or_404(Conge, pk=pk)
    if request.method == 'POST':
        form = CongeForm(request.POST, instance=conge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Congé mis à jour avec succès !')
            return redirect('conge_list')
    else:
        form = CongeForm(instance=conge)
    return render(request, 'conge_form.html', {'form': form})

# Vue pour supprimer un congé
@login_required
@user_passes_test(is_responsable_rh)
def conge_delete(request, pk):
    conge = get_object_or_404(Conge, pk=pk)
    if request.method == 'POST':
        conge.delete()
        messages.success(request, 'Congé supprimé avec succès !')
        return redirect('conge_list')
    return render(request, 'conge_confirm_delete.html', {'conge': conge})
# Vues pour les Salaires
@login_required
@user_passes_test(is_responsable_rh)
def salaire_list(request):
    salaires = Salaire.objects.all()
    return render(request, 'salaire_list.html', {'salaires': salaires})

@login_required
@user_passes_test(is_responsable_rh)
def salaire_create(request):
    if request.method == 'POST':
        form = SalaireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salaire enregistré avec succès !')
            return redirect('salaire_list')
    else:
        form = SalaireForm()
    return render(request, 'salaire_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def salaire_update(request, pk):
    salaire = get_object_or_404(Salaire, pk=pk)
    if request.method == 'POST':
        form = SalaireForm(request.POST, instance=salaire)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salaire mis à jour avec succès !')
            return redirect('salaire_list')
    else:
        form = SalaireForm(instance=salaire)
    return render(request, 'salaire_form.html', {'form': form})

@login_required 
@user_passes_test(is_responsable_rh)
def salaire_delete(request, pk):
    salaire = get_object_or_404(Salaire, pk=pk)
    if request.method == 'POST':
        salaire.delete()
        messages.success(request, 'Salaire supprimé avec succès !')
        return redirect('salaire_list')
    return render(request, 'salaire_confirm_delete.html', {'salaire': salaire})


# Vues pour le Recrutement
@login_required 
@user_passes_test(is_responsable_rh)
def recrutement_list(request):
    recrutements = Recrutement.objects.all()
    return render(request, 'recrutement_list.html', {'recrutements': recrutements})

@login_required
@user_passes_test(is_responsable_rh)
def recrutement_create(request):
    if request.method == 'POST':
        form = RecrutementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recrutement enregistré avec succès !')
            return redirect('recrutement_list')
    else:
        form = RecrutementForm()
    return render(request, 'recrutement_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def recrutement_update(request, pk):
    recrutement = get_object_or_404(Recrutement, pk=pk)
    if request.method == 'POST':
        form = RecrutementForm(request.POST, instance=recrutement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recrutement mis à jour avec succès !')
            return redirect('recrutement_list')
    else:
        form = RecrutementForm(instance=recrutement)
    return render(request, 'recrutement_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def recrutement_delete(request, pk):
    recrutement = get_object_or_404(Recrutement, pk=pk)
    if request.method == 'POST':
        recrutement.delete()
        messages.success(request, 'Recrutement supprimé avec succès !')
        return redirect('recrutement_list')
    return render(request, 'recrutement_confirm_delete.html', {'recrutement': recrutement})

# Vues pour les Évaluations
@login_required
def evaluation_list(request):
    """Affiche la liste des évaluations."""
    # Récupérer le profil de l'utilisateur
    try:
        profile = request.user.profile
        employes = Employe.objects.filter(profiles=profile)  
    except Profile.DoesNotExist:
        employes = Employe.objects.none()  

    if request.user.groups.filter(name='Responsables RH').exists() or request.user.groups.filter(name='Managers').exists():
        evaluations = Evaluation.objects.all()
    elif employes.exists():  
        evaluations = Evaluation.objects.filter(employe__in=employes)  
    else:
        evaluations = []  

    return render(request, 'evaluation_list.html', {'evaluations': evaluations})

@login_required
@user_passes_test(is_responsable_rh)
def evaluation_create(request):
    """Permet de créer une nouvelle évaluation."""
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)  
            evaluation.save()  
            messages.success(request, 'Évaluation enregistrée avec succès !')
            return redirect('evaluation_list')
        else:
            messages.error(request, 'Erreur lors de la création de l\'évaluation. Veuillez vérifier les informations saisies.')
    else:
        form = EvaluationForm()
    
    return render(request, 'evaluation_form.html', {'form': form})

@login_required 
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def evaluation_update(request, pk):
    """Permet de mettre à jour une évaluation existante."""
    evaluation = get_object_or_404(Evaluation, pk=pk)
    if request.method == 'POST':
        form = EvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Évaluation mise à jour avec succès !')
            return redirect('evaluation_list')
    else:
        form = EvaluationForm(instance=evaluation)
    return render(request, 'evaluation_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def evaluation_delete(request, pk):
    """Permet de supprimer une évaluation."""
    evaluation = get_object_or_404(Evaluation, pk=pk)
    if request.method == 'POST':
        evaluation.delete()
        messages.success(request, 'Évaluation supprimée avec succès !')
        return redirect('evaluation_list')
    return render(request, 'evaluation_confirm_delete.html', {'evaluation': evaluation})

@login_required
def evaluation_report(request, pk):
    """Génère un rapport d'évaluation pour une évaluation spécifique."""
    evaluation = get_object_or_404(Evaluation, pk=pk)
    return render(request, 'evaluation_report.html', {'evaluation': evaluation})

@login_required
def evaluation_detail(request, pk):
    """Affiche les détails d'une évaluation spécifique."""
    evaluation = get_object_or_404(Evaluation, pk=pk)
    return render(request, 'evaluation_detail.html', {'evaluation': evaluation})

# Vues pour les fiches d'employés
@login_required 
@user_passes_test(is_responsable_rh)
def fiche_employe_list(request):
    fiches = FicheEmploye.objects.all()
    return render(request, 'fiche_employe_list.html', {'fiches': fiches})

@login_required
def offre_emploi_public(request):
    offres = OffreEmploi.objects.filter(statut='active')  
    return render(request, 'offre_emploi_public.html', {'offres': offres})

@login_required
@user_passes_test(is_responsable_rh)
def fiche_employe_create(request):
    if request.method == 'POST':
        form = FicheEmployeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fiche d\'employé créée avec succès !')
            return redirect('fiche_employe_list')
    else:
        form = FicheEmployeForm()
    return render(request, 'fiche_employe_form.html', {'form': form})

@login_required 
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def fiche_employe_update(request, pk):
    fiche = get_object_or_404(FicheEmploye, pk=pk)
    if request.method == 'POST':
        form = FicheEmployeForm(request.POST, instance=fiche)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fiche d\'employé mise à jour avec succès !')
            return redirect('fiche_employe_list')
    else:
        form = FicheEmployeForm(instance=fiche)
    return render(request, 'fiche_employe_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def generer_fiches_paie(request):
    employes = Employe.objects.all()
    for employe in employes:
        salaire_final = calculer_salaire(employe)  
        fiche_paie = FichePaie(
            employe=employe,
            date_paiement=date.today(),
            salaire_base=employe.salaire_base,
            salaire_final=salaire_final
        )
        fiche_paie.save()
    messages.success(request, "Fiches de paie générées avec succès !")
    return redirect('fiche_paie_list') 

@login_required
@user_passes_test(is_responsable_rh)
def fiche_employe_delete(request, pk):
    fiche = get_object_or_404(FicheEmploye, pk=pk)
    if request.method == 'POST':
        fiche.delete()
        messages.success(request, 'Fiche d\'employé supprimée avec succès !')
        return redirect('fiche_employe_list')
    return render(request, 'fiche_employe_confirm_delete.html', {'fiche': fiche})

# Vues pour les Types de Congé
@login_required 
@user_passes_test(is_responsable_rh)
def type_conge_list(request):
    types_conge = TypeConge.objects.all()
    return render(request, 'type_conge_list.html', {'types_conge': types_conge})

@login_required
@user_passes_test(is_responsable_rh)
def type_conge_create(request):
    if request.method == 'POST':
        form = TypeCongeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de congé créé avec succès !')
            return redirect('type_conge_list')
    else:
        form = TypeCongeForm()
    return render(request, 'type_conge_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def type_conge_update(request, pk):
    type_conge = get_object_or_404(TypeConge, pk=pk)
    if request.method == 'POST':
        form = TypeCongeForm(request.POST, instance=type_conge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de congé mis à jour avec succès !')
            return redirect('type_conge_list')
    else:
        form = TypeCongeForm(instance=type_conge)
    return render(request, 'type_conge_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def type_conge_delete(request, pk):
    type_conge = get_object_or_404(TypeConge, pk=pk)
    if request.method == 'POST':
        type_conge.delete()
        messages.success(request, 'Type de congé supprimé avec succès !')
        return redirect('type_conge_list')
    return render(request, 'type_conge_confirm_delete.html', {'type_conge': type_conge})

@login_required 
def demander_conge(request):
    if request.method == 'POST':
        form = CongeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre demande de congé a été soumise avec succès !')
            return redirect('conge_list') 
        form = CongeForm()
    return render(request, 'demander_conge.html', {'form': form})

# Vues pour solde congé 

# Liste des Soldes de Congé
@login_required
@user_passes_test(is_responsable_rh)
def solde_conge_list(request):
    soldes = SoldeConge.objects.all()
    return render(request, 'solde_conge_list.html', {'soldes': soldes})

# Création d'un Solde de Congé
@login_required
@user_passes_test(is_responsable_rh)
def solde_conge_create(request):
    if request.method == 'POST':
        form = SoldeCongeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solde de congé créé avec succès !')
            return redirect('solde_conge_list')
    else:
        form = SoldeCongeForm()
    return render(request, 'solde_conge_form.html', {'form': form})

# Mise à jour d'un Solde de Congé
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def solde_conge_update(request, pk):
    solde_conge = get_object_or_404(SoldeConge, pk=pk)
    if request.method == 'POST':
        form = SoldeCongeForm(request.POST, instance=solde_conge)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solde de congé mis à jour avec succès !')
            return redirect('solde_conge_list')
    else:
        form = SoldeCongeForm(instance=solde_conge)
    return render(request, 'solde_conge_form.html', {'form': form})

# Suppression d'un Solde de Congé
@login_required
@user_passes_test(is_responsable_rh)
def solde_conge_delete(request, pk):
    solde_conge = get_object_or_404(SoldeConge, pk=pk)
    if request.method == 'POST':
        solde_conge.delete()
        messages.success(request, 'Solde de congé supprimé avec succès !')
        return redirect('solde_conge_list')
    return render(request, 'solde_conge_confirm_delete.html', {'solde_conge': solde_conge})



# Vues pour les fiches de paie
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u) or u.groups.filter(name='Utilisateurs').exists())
def fiche_paie_list(request):
    fiches = FichePaie.objects.all()  # Récupérer toutes les fiches de paie
    return render(request, 'fiche_paie_list.html', {'fiches': fiches})

# Vue pour créer une nouvelle fiche de paie
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u) or u.groups.filter(name='Utilisateurs').exists())
def fiche_paie_create(request):
    if request.method == 'POST':
        form = FichePaieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fiche de paie créée avec succès.")
            return redirect('fiche_paie_list')  
    else:
        form = FichePaieForm()
    return render(request, 'fiche_paie_form.html', {'form': form})

# Vue pour mettre à jour une fiche de paie existante
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u) or u.groups.filter(name='Utilisateurs').exists())
def fiche_paie_update(request, pk):
    fiche_paie = get_object_or_404(FichePaie, pk=pk)
    if request.method == 'POST':
        form = FichePaieForm(request.POST, instance=fiche_paie)
        if form.is_valid():
            form.save()
            messages.success(request, "Fiche de paie mise à jour avec succès.")
            return redirect('fiche_paie_list') 
    else:
        form = FichePaieForm(instance=fiche_paie)
    return render(request, 'fiche_paie_form.html', {'form': form})

# Vue pour supprimer une fiche de paie
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u) or u.groups.filter(name='Utilisateurs').exists())
def fiche_paie_delete(request, pk):
    fiche_paie = get_object_or_404(FichePaie, pk=pk)
    if request.method == 'POST':
        fiche_paie.delete()
        messages.success(request, "Fiche de paie supprimée avec succès.")
        return redirect('fiche_paie_list')  
    return render(request, 'fiche_paie_confirm_delete.html', {'fiche_paie': fiche_paie})

# Vue pour afficher les détails d'une fiche de paie
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u) or u.groups.filter(name='Utilisateurs').exists())
def fiche_paie_detail(request, pk):
    fiche_paie = get_object_or_404(FichePaie, pk=pk)
    return render(request, 'fiche_paie_detail.html', {'fiche': fiche_paie})

# Vue pour gérer la demande d'avance sur salaire
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or u.groups.filter(name='Utilisateurs').exists())
def demander_avance(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        justification = request.POST.get('justification')

        # Validation du montant
        if not montant or float(montant) <= 0:
            messages.error(request, "Le montant de l'avance doit être positif.")
            return render(request, 'demander_avance.html')

        # Créer une nouvelle demande d'avance
        avance = AvanceSalaire(
            employe=request.user.employe,  
            montant=float(montant),
            date_demande=date.today(),
            justification=justification
        )
        avance.save()

        messages.success(request, "Demande d'avance soumise avec succès.")
        return redirect('fiche_paie_list')  

    return render(request, 'demander_avance.html')

# Vues Pour Primes
@login_required 
@user_passes_test(is_responsable_rh)
def prime_list(request):
    primes = Prime.objects.all()
    return render(request, 'prime_list.html', {'primes': primes})

@login_required
@user_passes_test(is_responsable_rh)
def prime_create(request):
    if request.method == 'POST':
        form = PrimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prime ajoutée avec succès !')
            return redirect('prime_list')
    else:
        form = PrimeForm()
    return render(request, 'prime_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def prime_update(request, pk):
    prime = get_object_or_404(Prime, pk=pk)
    if request.method == 'POST':
        form = PrimeForm(request.POST, instance=prime)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prime mise à jour avec succès !')
            return redirect('prime_list')
    else:
        form = PrimeForm(instance=prime)
    return render(request, 'prime_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def prime_delete(request, pk):
    prime = get_object_or_404(Prime, pk=pk)
    if request.method == 'POST':
        prime.delete()
        messages.success(request, 'Prime supprimée avec succès !')
        return redirect('prime_list')
    return render(request, 'prime_confirm_delete.html', {'prime': prime})

# Vues pour Contrats
@login_required
def contrat_list(request):
    """Affiche la liste des contrats avec filtrage."""
    contrats = Contrat.objects.all()

    # Filtrage par service, plage de dates, type, etc.
    service_filter = request.GET.get('service')
    date_debut_filter = request.GET.get('date_debut')
    date_fin_filter = request.GET.get('date_fin')
    type_filter = request.GET.get('type')

    if service_filter:
        contrats = contrats.filter(employe__service__id=service_filter)
    if date_debut_filter:
        contrats = contrats.filter(date_debut__gte=date_debut_filter)
    if date_fin_filter:
        contrats = contrats.filter(date_fin__lte=date_fin_filter)
    if type_filter:
        contrats = contrats.filter(type_contrat=type_filter)

    # Vérification des rôles pour afficher les contrats
    if is_responsable_rh(request.user) or is_manager(request.user):
        return render(request, 'contrat_list.html', {'contrats': contrats})
    else:
        # Les utilisateurs voient uniquement leurs propres contrats
        employe_ = Employe.objects.get(email=request.user.username)
        contrats = contrats.filter(employe=employe_)
        return render(request, 'contrat_list.html', {'contrats': contrats})

@login_required
@user_passes_test(is_responsable_rh)
def contrat_create(request):
    """Permet de créer un nouveau contrat."""
    if request.method == 'POST':
        form = ContratForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrat créé avec succès !')
            return redirect('contrat_list')
    else:
        form = ContratForm()
    return render(request, 'contrat_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def contrat_update(request, pk):
    """Permet de mettre à jour un contrat existant."""
    contrat = get_object_or_404(Contrat, pk=pk)
    if request.method == 'POST':
        form = ContratForm(request.POST, instance=contrat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contrat mis à jour avec succès !')
            return redirect('contrat_list')
    else:
        form = ContratForm(instance=contrat)
    return render(request, 'contrat_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def contrat_delete(request, pk):
    """Permet de supprimer un contrat."""
    contrat = get_object_or_404(Contrat, pk=pk)
    if request.method == 'POST':
        # Crée une archive avant de supprimer le contrat
        ArchiveContrat.objects.create(contrat=contrat)  
        contrat.delete()  
        messages.success(request, 'Contrat supprimé et archivé avec succès !')
        return redirect('contrat_list')
    return render(request, 'contrat_confirm_delete.html', {'contrat': contrat})

@login_required
@user_passes_test(is_responsable_rh)
def contrat_detail(request, pk):
    """Affiche les détails d'un contrat spécifique."""
    contrat = get_object_or_404(Contrat, pk=pk)
    return render(request, 'contrat_detail.html', {'contrat': contrat})

# Vues pour types Contrats
@login_required
@user_passes_test(is_responsable_rh)
def type_contrat_list(request):
    type_contrats = TypeContrat.objects.all()
    return render(request, 'type_contrat_list.html', {'type_contrats': type_contrats})

@login_required
@user_passes_test(is_responsable_rh)
def type_contrat_create(request):
    if request.method == 'POST':
        form = TypeContratForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de contrat ajouté avec succès !')
            return redirect('type_contrat_list')
    else:
        form = TypeContratForm()
    return render(request, 'type_contrat_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def type_contrat_update(request, pk):
    type_contrat = get_object_or_404(TypeContrat, pk=pk)
    if request.method == 'POST':
        form = TypeContratForm(request.POST, instance=type_contrat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type de contrat mis à jour avec succès !')
            return redirect('type_contrat_list')
    else:
        form = TypeContratForm(instance=type_contrat)
    return render(request, 'type_contrat_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def type_contrat_delete(request, pk):
    type_contrat = get_object_or_404(TypeContrat, pk=pk)
    if request.method == 'POST':
        type_contrat.delete()
        messages.success(request, 'Type de contrat supprimé avec succès !')
        return redirect('type_contrat_list')
    return render(request, 'type_contrat_confirm_delete.html', {'type_contrat': type_contrat})
    
# Vues Pour archiver Contrat
@login_required
@user_passes_test(is_responsable_rh)
def archive_contrat_list(request):
    """Affiche la liste des archives de contrats."""
    archives = ArchiveContrat.objects.all()
    return render(request, 'archive_contrat_list.html', {'archives': archives})
@login_required
@user_passes_test(is_responsable_rh)
def archive_contrat_detail(request, pk):
    """Affiche les détails d'une archive de contrat spécifique."""
    archive = get_object_or_404(ArchiveContrat, pk=pk)
    return render(request, 'archive_contrat_detail.html', {'archive': archive})
@login_required
@user_passes_test(is_responsable_rh)
def archive_contrat_delete(request, pk):
    """Permet de supprimer une archive de contrat."""
    archive = get_object_or_404(ArchiveContrat, pk=pk)
    if request.method == 'POST':
        archive.delete()
        messages.success(request, 'Archive de contrat supprimée avec succès !')
        return redirect('archive_contrat_list')
    return render(request, 'archive_contrat_confirm_delete.html', {'archive': archive})
@login_required
@user_passes_test(is_responsable_rh)
def contrat_archive(request, pk):
    """Permet d'archiver un contrat."""
    contrat = get_object_or_404(Contrat, pk=pk)
    if request.method == 'POST':
        # Crée une archive avant de supprimer le contrat
        ArchiveContrat.objects.create(contrat=contrat)  
        messages.success(request, 'Contrat archivé avec succès !')
        return redirect('contrat_list')
    return render(request, 'contrat_confirm_archive.html', {'contrat': contrat})

# Vues pour offre d'emploi
def offre_emploi_list(request):
    """Affiche la liste des offres d'emploi pour tous les utilisateurs, connectés ou non."""
    offres = OffreEmploi.objects.all()
    return render(request, 'offre_emploi_list.html', {'offres': offres})

@login_required
@user_passes_test(is_responsable_rh)
def offre_emploi_create(request):
    """Permet de créer une nouvelle offre d'emploi."""
    if request.method == 'POST':
        form = OffreEmploiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offre d\'emploi créée avec succès !')
            return redirect('offre_emploi_list')
    else:
        form = OffreEmploiForm()
    return render(request, 'offre_emploi_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def offre_emploi_update(request, pk):
    """Permet de mettre à jour une offre d'emploi existante."""
    offre = get_object_or_404(OffreEmploi, pk=pk)
    if request.method == 'POST':
        form = OffreEmploiForm(request.POST, instance=offre)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offre d\'emploi mise à jour avec succès !')
            return redirect('offre_emploi_list')
    else:
        form = OffreEmploiForm(instance=offre)
    return render(request, 'offre_emploi_form.html', {'form': form})

@login_required
@user_passes_test(is_responsable_rh)
def offre_emploi_delete(request, pk):
    """Permet de supprimer une offre d'emploi."""
    offre = get_object_or_404(OffreEmploi, pk=pk)
    if request.method == 'POST':
        offre.delete()
        messages.success(request, 'Offre d\'emploi supprimée avec succès !')
        return redirect('offre_emploi_list')
    return render(request, 'offre_emploi_confirm_delete.html', {'offre': offre})

# Vues pour les condidats 
def candidature_create(request, offre_id):
    offre = get_object_or_404(OffreEmploi, pk=offre_id)
    
    if request.method == 'POST':
        form = CandidatureForm(request.POST, request.FILES)
        if form.is_valid():
            candidature = form.save(commit=False)  
            candidature.offre = offre  
            candidature.statut = 'en_cours'  
            candidature.save()  
            messages.success(request, 'Candidature soumise avec succès !')
            return redirect('candidats_list')  
        else:
            messages.error(request, 'Erreur lors de la soumission de la candidature. Veuillez vérifier les informations.')
    else:
        form = CandidatureForm()
    
    return render(request, 'candidature_form.html', {'form': form, 'offre': offre})
# Vue pour mettre à jour le statut d'une 
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def candidats_list(request):
    """Affiche la liste des candidatures avec des actions pour chaque candidature."""
    candidatures = Candidature.objects.all()
    return render(request, 'candidats_list.html', {'candidatures': candidatures})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def changer_statut_candidature(request, pk):
    candidature = get_object_or_404(Candidature, pk=pk)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        candidature.statut = nouveau_statut
        candidature.save()

        # Vérifiez si le candidat existe avant d'envoyer l'e-mail
        if candidature.candidat and candidature.candidat.email:
            envoyer_notification_candidature(candidature.candidat.email, candidature.offre.titre, nouveau_statut)
        else:
            messages.warning(request, "Le candidat n'a pas d'adresse e-mail associée.")

        messages.success(request, 'Statut de la candidature mis à jour !')
        return redirect('candidats_list')

    return render(request, 'changer_statut.html', {'candidature': candidature})

@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def mise_a_jour_statut_candidature(request, pk):
    candidature = get_object_or_404(Candidature, pk=pk)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')  
        candidature.statut = nouveau_statut
        candidature.save()
        
        # Envoyer une notification par e-mail
        envoyer_notification_candidature(candidature.candidat.email, candidature.offre.titre, nouveau_statut)
        
        messages.success(request, 'Statut de la candidature mis à jour et notification envoyée !')
        return redirect('candidature_list')
    
    return render(request, 'mise_a_jour_statut.html', {'candidature': candidature})

@login_required
@user_passes_test(is_responsable_rh)
def candidature_delete(request, pk):
    """Permet de supprimer une candidature."""
    candidature = get_object_or_404(Candidature, pk=pk)
    if request.method == 'POST':
        candidature.delete()
        messages.success(request, 'Candidature supprimée avec succès !')
        return redirect('candidats_list')
    return render(request, 'candidature_confirm_delete.html', {'candidature': candidature})
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def liste_cvs(request):
    candidatures = Candidature.objects.all()
    return render(request, 'liste_cvs.html', {'candidatures': candidatures})

#  Vue pour Afficher les Entretiens
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def entretien_list(request):
    """Affiche la liste des entretiens."""
    entretiens = Entretien.objects.all()
    return render(request, 'entretien_list.html', {'entretiens': entretiens, 'candidature_id': candidats_list})

# Vue pour ajouter un entretien 
@login_required
@user_passes_test(is_responsable_rh)
def entretien_update(request, pk):
    """Permet de mettre à jour un entretien existant."""
    entretien = get_object_or_404(Entretien, pk=pk)
    if request.method == 'POST':
        form = EntretienForm(request.POST, instance=entretien)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entretien mis à jour avec succès !')
            return redirect('entretien_list')
    else:
        form = EntretienForm(instance=entretien)  
    return render(request, 'entretien_form.html', {'form': form, 'entretien': entretien})

@login_required
@user_passes_test(is_responsable_rh)
def entretien_create(request, candidature_id):
    """Permet de créer un nouvel entretien pour une candidature."""
    candidature = get_object_or_404(Candidature, pk=candidature_id)
    if request.method == 'POST':
        form = EntretienForm(request.POST)
        if form.is_valid():
            entretien = form.save(commit=False)
            entretien.candidature = candidature
            entretien.save()

            # Vérifiez que le candidat et l'offre existent avant d'envoyer l'e-mail
            if candidature.candidat and candidature.offre:
                envoyer_notification_entretien(
                    candidature.candidat.email,
                    candidature.offre.titre,
                    entretien.date_entretien,
                    entretien.heure_entretien,
                    entretien.lieu
                )
                messages.success(request, 'Entretien planifié avec succès et notification envoyée !')
            else:
                messages.warning(request, 'Entretien planifié, mais impossible d\'envoyer la notification.')

            return redirect('entretien_list')  
    else:
        form = EntretienForm()
    return render(request, 'entretien_form.html', {'form': form, 'candidature': candidature})
@login_required
@user_passes_test(is_responsable_rh)
def entretien_delete(request, pk):
    """Permet de supprimer un entretien existant."""
    entretien = get_object_or_404(Entretien, pk=pk)
    if request.method == 'POST':
        entretien.delete()
        messages.success(request, 'Entretien supprimé avec succès !')
        return redirect('entretien_list')
    return render(request, 'entretien_confirm_delete.html', {'entretien': entretien})

def entretien_list(request):
    """Affiche la liste des entretiens."""
    entretiens = Entretien.objects.all()
    return render(request, 'entretien_list.html', {'entretiens': entretiens})

# Vues pour les Absences
@login_required
def marquer_absence(request):
    """Permet à un employé de marquer une absence."""
    if request.method == 'POST':
        form = AbsenceForm(request.POST)  
        if form.is_valid():
            form.save()  
            messages.success(request, 'Absence marquée avec succès !')  
            return redirect('liste_absences')  
    else:
        form = AbsenceForm()  
    return render(request, 'marquer_absence.html', {'form': form})  


@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def liste_absences(request):
    """Affiche la liste des absences pour tous les employés."""
    absences = Absence.objects.all()  
    return render(request, 'liste_absences.html', {'absences': absences})
# Vues pour les Retards
@login_required
def marquer_retard(request):
    """Permet à un employé de marquer un retard."""
    if request.method == 'POST':
        form = RetardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Retard marqué avec succès !')
            return redirect('liste_retards')  
    else:
        form = RetardForm()
    return render(request, 'marquer_retard.html', {'form': form})
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def liste_retards(request):
    """Affiche la liste des retards pour tous les employés."""
    retards = Retard.objects.all()  
    return render(request, 'liste_retards.html', {'retards': retards})


# Vues pour tableau de bord
@login_required
@user_passes_test(lambda u : is_responsable_rh(u) or is_manager(u))
def dashboard(request):
    return render(request, 'dashboard.html')
@login_required
@user_passes_test(lambda u: is_responsable_rh(u) or is_manager(u))
def tableau_de_bord(request):
    try:
        # Comptage des entités
        employe_count = Employe.objects.count()
        conge_count = Conge.objects.count()
        contrat_count = Contrat.objects.count()
        salaire_count = Salaire.objects.count()
        recrutement_count = Recrutement.objects.count()
        evaluation_count = Evaluation.objects.count()

        # Analyse des employés
        effectifs_par_contrat = Employe.objects.values('type_contrat').annotate(count=Count('id'))
        sexe_distribution = Employe.objects.values('sexe').annotate(count=Count('id'))
        age_distribution = {
            'moins_de_30': Employe.objects.filter(date_naissance__gt=timezone.now().year - 30).count(),
            'entre_30_et_50': Employe.objects.filter(date_naissance__lte=timezone.now().year - 30, date_naissance__gt=timezone.now().year - 50).count(),
            'plus_de_50': Employe.objects.filter(date_naissance__lte=timezone.now().year - 50).count(),
        }
        top_performeurs = Evaluation.objects.order_by('-score')[:5]

        # Analyse d'activité : Pics d'absences
        absences = Absence.objects.values('date_absence').annotate(count=Count('id')).order_by('date_absence')
        dates = [absence['date_absence'].strftime('%Y-%m-%d') for absence in absences]
        counts = [absence['count'] for absence in absences]

        # Préparer les données d'absence
        absence_data = {
            'dates': dates,
            'counts': counts,
        }
        absence_data_json = json.dumps(absence_data)

        # Création d'un graphique
        plt.figure(figsize=(10, 5))
        plt.plot(dates, counts, marker='o')
        plt.title('Pics d\'Absences')
        plt.xlabel('Date')
        plt.ylabel('Nombre d\'Absences')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Sauvegarde du graphique dans un objet BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        image_png = buf.getvalue()  
        buf.close()
        graphic = base64.b64encode(image_png).decode('utf-8')

        # Analyse des recrutements sur 12 mois
        recrutements_par_mois = (
            Recrutement.objects
            .filter(date_recrutement__gte=timezone.now() - timezone.timedelta(days=365))
            .annotate(month=TruncMonth('date_recrutement'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Calculer le taux d'évolution des recrutements
        taux_recrutement = []
        for i in range(1, len(recrutements_par_mois)):
            if recrutements_par_mois[i-1]['count'] > 0:  
                evolution = (
                    (recrutements_par_mois[i]['count'] - recrutements_par_mois[i-1]['count']) /
                    recrutements_par_mois[i-1]['count'] * 100
                )
                taux_recrutement.append({
                    'month': recrutements_par_mois[i]['month']. strftime('%Y-%m'),
                    'evolution': evolution
                })

        # Préparer les données pour le template
        context = {
    'employe_count': employe_count,
    'conge_count': conge_count,
    'contrat_count': contrat_count,
    'salaire_count': salaire_count,
    'recrutement_count': recrutement_count,
    'evaluation_count': evaluation_count,
    'effectifs_par_contrat': effectifs_par_contrat,
    'sexe_distribution': sexe_distribution,
    'age_distribution': age_distribution,
    'top_performeurs': top_performeurs,
    'graphic': graphic,
    'absence_data': absence_data_json,
    'taux_recrutement': taux_recrutement,
    'candidatures': Candidature.objects.all()  
}

        return render(request, 'tableau_de_bord.html', context)

    except Exception as e:
        messages.error(request, f"Une erreur s'est produite : {str(e)}")
        return render(request, 'tableau_de_bord.html', {})
    
# Vues pour calendrier
class EventMonthArchiveView(MonthArchiveView):
    model = Event
    date_field = 'date'
    template_name = 'event_month_archive.html'
    context_object_name = 'events'
    allow_future = True 
class EventDayArchiveView(ListView):
    model = Event
    template_name = 'event_day_archive.html'
    
    def get_queryset(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        day = self.kwargs['day']
        date = datetime(year, month, day)  
        return Event.objects.filter(date=date)

class EventYearArchiveView(YearArchiveView):
    model = Event
    date_field = 'date'
    template_name = 'event_year_archive.html'
    context_object_name = 'events'
    allow_future = True
@login_required
def calendar_view(request, year=None, month=None):
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    else:
        year = int(year)
        month = int(month)

    # Gérer le changement de mois
    if month < 1: 
        month = 12
        year -= 1
    elif month > 12:  
        month = 1
        year += 1

    # Créer un calendrier pour le mois spécifié
    cal = calendar.monthcalendar(year, month)

    # Récupérer les événements pour le mois
    events = Event.objects.filter(date__year=year, date__month=month)

    # Créer un ensemble de jours avec des événements
    event_days = {event.date.day for event in events}

    context = {
        'calendar': cal,
        'year': year,
        'month': month,
        'events': events,
        'month_name': calendar.month_name[month],
        'event_days': event_days,
    }
    
    return render(request, 'calendar.html', context)

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    template_name = 'event_form.html'
    fields = ['title', 'date', 'description']  
    success_url = reverse_lazy('calendar_view')  

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        return is_responsable_rh(self.request.user)  
class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'event_confirm_delete.html'  
    success_url = reverse_lazy('calendar_view')  

    def test_func(self):
        
        return is_responsable_rh(self.request.user)

@login_required
@user_passes_test(is_responsable_rh)
def event_list(request):
    events = Event.objects.all()  
    context = {
        'events': events,
    }
    return render(request, 'event_list.html', context)
@login_required
@user_passes_test(is_responsable_rh)
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list') 
    else:
        form = EventForm(instance=event)
    
    return render(request, 'event_edit.html', {'form': form, 'event': event})

# Vues pour les Messages
@login_required
def some_view(request):
    User = get_user_model()  
    users = User.objects.all() 
    return render(request, 'some_template.html', {'users': users})
@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()

          
            profile = get_object_or_404(Profile, user=request.user)

            if profile.is_responsable_rh:
                all_employees = User.objects.all()
                for employee in all_employees:
                    send_mail(
                        message.subject,
                        message.body,
                        request.user.email,  
                        [employee.email],  
                    )
                    create_notification(employee, f"Vous avez reçu un nouveau message de {request.user.username}: {message.subject}")

            elif profile.is_responsable_service:
                team_members = User.objects.filter(profile__employe__department=request.user.profile.employe.department)
                for member in team_members:
                    send_mail(
                        message.subject,
                        message.body,
                        request.user.email,  
                        [member.email],  
                    )
                    create_notification(member, f"Vous avez reçu un nouveau message de {request.user.username}: {message.subject}")

            # Ajoutez un message de succès
            messages.success(request, "Votre message a été envoyé avec succès.")
            return redirect('inbox')  
    else:
        form = MessageForm()
    return render(request, 'send_message.html', {'form': form})
@login_required
def inbox(request):
    
    messages = Message.objects.filter(recipient=request.user)
    return render(request, 'inbox.html', {'messages': messages})
@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    return render(request, 'view_message.html', {'message': message})  
@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.delete()
    return redirect('inbox')  

# Vues pour Notifiation
@login_required
def create_notification(user, message):
    Notification.objects.create(user=user, message=message)
@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'notifications.html', {'notifications': user_notifications})
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')  

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('notifications') 

from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import  send_mail, BadHeaderError
from .models import  Absence, AvanceSalaire , Conge, Contrat, Prime, SoldeConge
from django.utils import timezone


# Met à jour le solde de congé de l'employé
def mettre_a_jour_solde_conge(employe):
    try:
        # Récupérer le solde de congé de l'employé
        solde_conge = employe.soldeconge
        
        # Calculer le solde restant
        solde_conge.solde_restant = solde_conge.solde_initial - solde_conge.solde_utilise
        
        # Enregistrer les modifications
        solde_conge.save()

    except SoldeConge.DoesNotExist:
        raise ValidationError("Aucun solde de congé trouvé pour cet employé.")

# Calcule le solde restant
def calculer_solde_restant(solde_conge):
    return solde_conge.solde_initial - solde_conge.solde_utilise

# Approuve une demande de congé
def approuver_conge(conge):
    # Valider le congé avant de procéder
    conge.full_clean()  

    try:
        # Récupérer le solde de congé de l'employé
        solde_conge = conge.employe.soldeconge
        
        # Vérifier si le nombre de jours utilisés dépasse le solde restant
        if conge.jours_utilises > solde_conge.solde_restant:
            raise ValidationError("Le nombre de jours demandés dépasse le solde restant.")

        # Mettre à jour le solde de congé
        solde_conge.solde_utilise += conge.jours_utilises
        solde_conge.save()  

        # Enregistrer le congé
        conge.save()  

    except SoldeConge.DoesNotExist:
        raise ValidationError("Aucun solde de congé trouvé pour cet employé.")

# Demande un congé pour un employé
def demander_conge(employe, type_conge, date_debut, date_fin):
    # Calculer le nombre de jours entre date_debut et date_fin
    jours_utilises = (date_fin - date_debut).days + 1 

    if jours_utilises <= 0:
        raise ValidationError("La date de fin doit être postérieure à la date de début.")

    conge = Conge(employe=employe, type_conge=type_conge, date_debut=date_debut, date_fin=date_fin, jours_utilises=jours_utilises)
    conge.full_clean()  # Valide le congé avant de procéder

    try:
        solde_conge = employe.soldeconge
        if jours_utilises > solde_conge.solde_restant:
            raise ValidationError("Le nombre de jours demandés dépasse le solde restant.")

        # Mettre à jour le solde de congé
        solde_conge.solde_utilise += jours_utilises
        solde_conge.save()  

        # Enregistrer le congé
        conge.save()  

    except SoldeConge.DoesNotExist:
        raise ValidationError("Aucun solde de congé trouvé pour cet employé.")

# Calcule les salaires 
def calculer_salaire(employe):
    salaire_base = employe.salaire_base
    absences = Absence.objects.filter(employe=employe)
    avances = AvanceSalaire.objects.filter(employe=employe)
    primes = Prime.objects.filter(employe=employe)  
    n = 30  

    # Calcul du salaire journalier
    salaire_journalier = salaire_base / n

    # Créer une liste pour représenter les jours du mois
    jours_absences = [0] * n 

    # Marquer les jours d'absence
    for absence in absences:
        jour_du_mois = absence.date_absence.day - 1  
        if 0 <= jour_du_mois < n:
            jours_absences[jour_du_mois] = 1  

    # Calculer le nombre total d'absences
    total_absences = sum(jours_absences)

    # Calcul du montant des avances
    total_avances = sum(avance.montant for avance in avances)

    # Calcul du montant des primes
    total_primes = sum(prime.montant for prime in primes)

    # Calcul du salaire final
    salaire_final = salaire_base - (total_absences * salaire_journalier) - total_avances + total_primes

    return salaire_final
# Pour Contrat
def check_periods_of_trial():
    today = timezone.now().date()
    contrats = Contrat.objects.filter(date_debut__lte=today, date_fin__gte=today)
    for contrat in contrats:
        if contrat.periode_essai and (today - contrat.date_debut).days >= contrat.periode_essai:
            # Notification  pour le responsable RH
            print(f"Alerte : La période d'essai de {contrat.employe} se termine bientôt.")

# Fonction pour Envoyer des E-Mails Pour Les Condidats 
def envoyer_notification_candidature(nom_candidat, candidat_email, offre_titre, statut):
    subject = f"État de votre candidature pour {offre_titre}"
    message = f"Bonjour {nom_candidat},\n\nVotre candidature pour l'offre '{offre_titre}' a été mise à jour. État actuel : {statut}.\n\nCordialement,\nL'équipe RH."
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(subject, message, from_email, [candidat_email])
    except BadHeaderError:
        print("Erreur dans l'en-tête de l'e-mail.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'envoi de l'e-mail : {e}")
# Fonction pour Envoyer des E_Mails Pour les  Entretiens
def envoyer_notification_entretien(candidat_email, offre_titre, date_entretien, heure_entretien, lieu):
    subject = f"Confirmation de votre entretien pour {offre_titre}"
    message = (
        f"Bonjour,\n\n"
        f"Nous vous confirmons que votre entretien pour l'offre '{offre_titre}' est prévu le {date_entretien} à {heure_entretien}.\n"
        f"Lieu : {lieu}\n\n"
        f"Cordialement,\nL'équipe RH."
    )
    from_email = settings.EMAIL_HOST_USER

    send_mail(subject, message, from_email, [candidat_email])

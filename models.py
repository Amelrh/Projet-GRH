from cProfile import Profile
from datetime import date, timezone
from urllib import request 
from django.conf import settings
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

# Inscription
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    first_name = forms.CharField(max_length=30, label="Nom")
    last_name = forms.CharField(max_length=30, label="Prénom")
    company_name = forms.CharField(max_length=255, label="Nom de la société")
    employee_id = forms.CharField(max_length=10, label="ID de l'employé")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'company_name', 'employee_id']
        labels = {
            'username': 'Nom d\'utilisateur',
            'email': 'Adresse e-mail',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                employee_id=self.cleaned_data['employee_id']
            )
        return user

# Les fonctionnalités
class Fonctionnalite(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom de la fonctionnalité")
    description = models.TextField(verbose_name="Description de la fonctionnalité")

    class Meta:
        verbose_name = "Fonctionnalité"
        verbose_name_plural = "Fonctionnalités"
        ordering = ['nom']

    def __str__(self):
        return self.nom

# Les favoris
class Favoris(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris', verbose_name="Utilisateur")
    fonctionnalite = models.ForeignKey(Fonctionnalite, on_delete=models.CASCADE, related_name='favoris', verbose_name="Fonctionnalité")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        unique_together = ('user', 'fonctionnalite')
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        ordering = ['-date_ajout']  

    def __str__(self):
        return f"{self.user.username} a ajouté {self.fonctionnalite.nom} aux favoris le {self.date_ajout.strftime('%Y-%m-%d %H:%M:%S')}"

# Les services
class Service(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code du service")
    nom = models.CharField(max_length=100, verbose_name="Nom du service")  
    description = models.TextField(verbose_name="Description du service")
    responsable = models.CharField(max_length=100, blank=True, verbose_name="Responsable")  
    date_creation = models.DateField(auto_now_add=True,null=True, verbose_name="Date de création")  
    email_responsable = models.CharField(max_length=40, null=True, verbose_name="Adresse e-mail du responsable")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return f"{self.nom} (Code: {self.code}) ({self.responsable}) ({self.email_responsable})"
    
# Les employés
class Employe(models.Model):
    TYPE_CONTRAT_CHOICES = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('STAGIAIRE', 'Stagiaire'),
    ]
    SEXE_CHOICES = [
        ('H', 'Homme'),
        ('F', 'Femme'),
    ] 
    code = models.CharField(max_length=10, unique=True, verbose_name="Code de l'employé") 
    nom = models.CharField(max_length=50, verbose_name="Nom")
    prenom = models.CharField(max_length=50, verbose_name="Prénom")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, null=True, blank=True, verbose_name="Sexe")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    date_embauche = models.DateField(verbose_name="Date d'embauche")
    adresse = models.TextField(verbose_name="Adresse")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='employes', verbose_name="Service")
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Salaire de base") 
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT_CHOICES, null=True, verbose_name="Type de contrat") 
    email = models.CharField(max_length=100, verbose_name="Adresse e-mail", default="prenom.nom@service.com")
    password = models.CharField(max_length=20, verbose_name="Mot de passe", default='password')

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['nom', 'prenom']
       

    def __str__(self):
        return f"{self.nom} {self.prenom} (Code: {self.code})"


    def age(self):
        """Calculer l'âge de l'employé."""
        return timezone.now().year - self.date_naissance.year - ((timezone.now().month, timezone.now().day) < (self.date_naissance.month, self.date_naissance.day))

    def anciennete(self):
        """Calculer l'ancienneté de l'employé en années."""
        return timezone.now().year - self.date_embauche.year - ((timezone.now().month, timezone.now().day) < (self.date_embauche.month, self.date_embauche.day))
    
    def extraire_premiers_caracteres(self): 
        mots = self.service.nom.split() 
        if len(mots) == 1: 
            return self.service.nom 
        result = ''.join([mot[0] for mot in mots]) 
        return result
        
    def save(self, *args, **kwargs): 
        self.email = f"{self.prenom.lower()}.{self.nom.lower()}@{self.extraire_premiers_caracteres()}.com" 
        self.password = f"{self.code}{self.prenom[0].upper()}{self.nom[0].upper()}{self.date_embauche.year}"
        super().save(*args, **kwargs)

class MessagePourEmploye(models.Model):
    employe = models.ForeignKey(Employe , on_delete=models.CASCADE, verbose_name="Employe")
    destinateur = models.CharField(max_length=100, blank=True, verbose_name="Destinateur")  
    objet = models.CharField(max_length=20, verbose_name="Objet")
    dateMessage = models.DateField(auto_now_add=True, verbose_name="Date du message")
    contenu = models.CharField(max_length=100, verbose_name="Contenu du message")

    def __str__(self):
        return self.objet
    
    def save(self, *args, **kwargs):
        # Sauvegarder la date d'envoi du message
        self.destinateur = self.employe.service.responsable
        super().save(*args, **kwargs)

# Profile 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='profiles', null=True, blank=True)
    is_responsable_rh = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_responsable_service = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    def __str__(self):
        return self.user.username
    
# Les types de congés
class TypeConge(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code du type de congé")
    description = models.CharField(max_length=100, verbose_name="Description")
    jours_par_an = models.PositiveIntegerField(verbose_name="Jours par an")
    cumulable = models.BooleanField(default=False, verbose_name="Cumulable")  

    class Meta:
        verbose_name = "Type de Congé"
        verbose_name_plural = "Types de Congés"

    def __str__(self):
        return f"{self.code} - {self.description}"

    def jours_restants(self, employe):
        total_pris = employe.conges.filter(type_conge=self).aggregate(total=models.Sum('jours_utilises'))['total'] or 0
        return self.jours_par_an - total_pris
# Le solde de congés
class SoldeConge(models.Model):
    employe = models.OneToOneField(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    type_conge = models.ForeignKey(TypeConge, on_delete=models.CASCADE, verbose_name="Type de Congé")
    solde_initial = models.PositiveIntegerField(verbose_name="Solde initial")
    solde_utilise = models.PositiveIntegerField(default=0, verbose_name="Solde utilisé") 
    solde_restant = models.PositiveIntegerField(default=0, verbose_name="Solde restant", editable=False)  

    class Meta:
        verbose_name = "Solde de Congé"
        verbose_name_plural = "Soldes de Congés"
    
    def save(self, *args, **kwargs):
        if self.solde_restant == 0:
            self.solde_restant = self.solde_initial - self.solde_utilise
        super().save(*args, **kwargs)
            

    def __str__(self):
        return f"Solde de {self.employe} pour {self.type_conge}"

# Les congés
class Conge(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    type_conge = models.ForeignKey(TypeConge, on_delete=models.CASCADE, verbose_name="Type de Congé")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    jours_utilises = models.PositiveIntegerField(default=0, verbose_name="Jours utilisés")

    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
        ordering = ['date_debut']

    def clean(self):
        if self.date_fin < self.date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")

        solde_conge = SoldeConge.objects.filter(employe=self.employe)
        if not solde_conge.exists():
            raise ValidationError("Aucun solde de congé trouvé pour cet employé.")

    def save(self, *args, **kwargs):
        self.jours_utilises = self.calculer_duree()
        self.full_clean()  
        super().save(*args, **kwargs)

    def calculer_duree(self):
        return (self.date_fin - self.date_debut).days + 1  

    def approuver_conge(self):
        self.full_clean()  
        try:
            solde_conge = self.employe.soldeconge
            solde_conge.solde_utilise += self.jours_utilises
            solde_conge.save()  
            self.save()  
        except SoldeConge.DoesNotExist:
            raise ValidationError("Aucun solde de congé trouvé pour cet employé.")

    def __str__(self):
        return f"Congé de {self.employe} du {self.date_debut} au {self.date_fin} ({self.jours_utilises} jours)"

# Les salaires
class Salaire(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='salaires', verbose_name="Employé")
    date_paiement = models.DateField(verbose_name="Date de paiement")
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Salaire de base")
    heures_supplementaires = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Heures supplémentaires")
    primes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Primes")
    salaire_final = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Salaire final", editable=False)  

    def save(self, *args, **kwargs):
        self.salaire_final = self.calculer_salaire_final()
        super().save(*args, **kwargs)

    def calculer_salaire_final(self):
        taux_horaire = Decimal(self.salaire_base) / 160  # on suppose 160 heures par mois
        return Decimal(self.salaire_base) + Decimal(self.primes) + (Decimal(self.heures_supplementaires) * taux_horaire)

    def __str__(self):
        return f"Salaire de {self.employe} pour le {self.date_paiement}"
# Les primes 
class Prime(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='primes', verbose_name="Employé")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    date_attribution = models.DateField(verbose_name="Date d'attribution")
    description = models.TextField(verbose_name="Description", blank=True)

    class Meta:
        verbose_name = "Prime"
        verbose_name_plural = "Primes"

    def __str__(self):
        return f"Prime de {self.montant} € pour {self.employe} le {self.date_attribution}"

# Le recrutement
class Recrutement(models.Model):
    employe = models.OneToOneField(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    date_recrutement = models.DateField(verbose_name="Date de recrutement")
    poste = models.CharField(max_length=50, verbose_name="Poste")
    statut = models.CharField(max_length=20, choices=[('en_cours', 'En cours'), ('termine', 'Terminé')], verbose_name="Statut")

    class Meta:
        verbose_name = "Recrutement"
        verbose_name_plural = "Recrutements"

    def clean(self):
        if self.date_recrutement > date.today():
            raise ValidationError("La date de recrutement ne peut pas être dans le futur.")

    def __str__(self):
        return f"Recrutement de {self.employe} pour le poste de {self.poste} le {self.date_recrutement}"

# La fiche d'employé
class FicheEmploye(models.Model):
    employe = models.OneToOneField(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    competences = models.TextField(verbose_name="Compétences", blank=True)
    formations = models.TextField(verbose_name="Formations", blank=True)
    historique_professionnel = models.TextField(verbose_name="Historique Professionnel", blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création", null=True)

    class Meta:
        verbose_name = "Fiche Employé"
        verbose_name_plural = "Fiches Employés"

    def __str__(self):
        return f"Fiche de {self.employe.nom} {self.employe.prenom}"

# Les évaluations
class Evaluation(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='evaluations', verbose_name="Employé")
    date_evaluation = models.DateField(verbose_name="Date de l'évaluation")
    objectifs_atteints = models.TextField(verbose_name="Objectifs atteints", blank=True)
    competences_developpees = models.TextField(verbose_name="Compétences développées", blank=True)
    note = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Note", null=True, blank=True)
    criteres = models.JSONField(verbose_name="Critères d'évaluation", default=dict, blank=True) 

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        ordering = ['-date_evaluation']

    def clean(self):
        if self.date_evaluation > date.today():
            raise ValidationError("La date de l'évaluation ne peut pas être dans le futur.")

    def __str__(self):
        return f"Évaluation de {self.employe} le {self.date_evaluation.strftime('%Y-%m-%d')}"

# Les absences 
class Absence(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='absences', verbose_name="Employé")
    date_absence = models.DateField(verbose_name="Date d'absence")
    justification = models.TextField(blank=True, null=True, verbose_name="Justification")
    justificatif = models.FileField(upload_to='justificatifs/absences/', blank=True, null=True, verbose_name="Justificatif") 

    class Meta:
        verbose_name = "Absence"
        verbose_name_plural = "Absences"
        permissions = [
            ("mark_absence", "Peut marquer une absence"),
        ]

    def __str__(self):
        return f'Absence de {self.employe.nom} le {self.date_absence}'

# Les retards
class Retard(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='retards', verbose_name="Employé")
    date_retard = models.DateField(verbose_name="Date de retard")
    heures_retard = models.PositiveIntegerField(verbose_name="Heures de retard", default=0)
    justification = models.TextField(blank=True, null=True, verbose_name="Justification")
    justificatif = models.FileField(upload_to='justificatifs/retards/', blank=True, null=True, verbose_name="Justificatif")  # Nouveau champ

    class Meta:
        verbose_name = "Retard"
        verbose_name_plural = "Retards"
        permissions = [
            ("mark_retard", "Peut marquer un retard"),
        ]

    def __str__(self):
        return f'Retard de {self.employe.nom} le {self.date_retard} ({self.heures_retard} heures)'

# Les avances sur salaire
class AvanceSalaire(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='avances', verbose_name="Employé")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    date_demande = models.DateField(verbose_name="Date de demande")
    justification = models.TextField(verbose_name="Justification")

    class Meta:
        verbose_name = "Avance sur Salaire"
        verbose_name_plural = "Avances sur Salaires"

    def clean(self):
        if self.montant <= 0:
            raise ValidationError("Le montant de l'avance doit être positif.")

    def __str__(self):
        return f'Avance de {self.montant} € pour {self.employe.nom} le {self.date_demande}'

# Les fiches de paie
class FichePaie(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE , related_name='fiches_paie', verbose_name="Employé")
    date_paiement = models.DateField(verbose_name="Date de paiement")
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire de base")
    salaire_final = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire final")

    class Meta:
        verbose_name = "Fiche de Paie"
        verbose_name_plural = "Fiches de Paie"

    def clean(self):
        if self.date_paiement > date.today():
            raise ValidationError("La date de paiement ne peut pas être dans le futur.")

    def __str__(self):
        return f'Fiche de Paie de {self.employe.nom} pour le {self.date_paiement}'
# Les type de contrats
class TypeContrat(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Code du type de contrat")
    nom = models.CharField(max_length=50, verbose_name="Nom du type de contrat",  null=True)  
    description = models.CharField(max_length=100, verbose_name="Description")

    class Meta:
        verbose_name = "Type de Contrat"
        verbose_name_plural = "Types de Contrats"

    def __str__(self):
        return f"{self.code} - {self.description}"  
       
# Les contrats    
class Contrat(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='contrats', verbose_name="Employé")
    type_contrat = models.ForeignKey(TypeContrat, on_delete=models.CASCADE, verbose_name="Type de contrat")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    periode_essai = models.IntegerField(null=True, blank=True, verbose_name="Période d'essai (en jours)")
    renouvellement = models.BooleanField(default=False, verbose_name="Renouvellement")

    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
        ordering = ['date_debut']

    def clean(self):
        if self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")

    def __str__(self):
        return f"Contrat {self.type_contrat} de {self.employe} du {self.date_debut} au {self.date_fin or 'indéfini'}"
    
# Les archives des contrats
class ArchiveContrat(models.Model):
    contrat = models.ForeignKey(Contrat, on_delete=models.CASCADE, related_name='archives', verbose_name="Contrat")
    date_archivage = models.DateField(auto_now_add=True, verbose_name="Date d'archivage")

    class Meta:
        verbose_name = "Archive de Contrat"
        verbose_name_plural = "Archives de Contrats"

    def __str__(self):
        return f"{self.contrat.type_contrat} - {self.date_archivage}"

    
# Les Offres d'Emplois
class OffreEmploi(models.Model):
    titre = models.CharField(max_length=255, verbose_name="Titre de l'offre")
    description = models.TextField(verbose_name="Description de l'offre")
    date_publication = models.DateField(auto_now_add=True, verbose_name="Date de publication")
    date_expiration = models.DateField(verbose_name="Date d'expiration")
    statut = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', verbose_name="Statut")

    class Meta:
        verbose_name = "Offre d'Emploi"
        verbose_name_plural = "Offres d'Emploi"

    def __str__(self):
        return self.titre

# Les condidats 
class Candidature(models.Model):
    offre = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE, related_name='candidatures', verbose_name="Offre d'emploi")
    candidat = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Candidat", null=True) 
    nom = models.CharField(max_length=50, verbose_name="Nom", null=True)
    prenom = models.CharField(max_length=50, verbose_name="Prénom", null=True)
    email = models.EmailField(default='default@example.com', verbose_name="Email")  
    cv = models.FileField(upload_to='', verbose_name="CV") 
    date_candidature = models.DateField(auto_now_add=True, verbose_name="Date de candidature")
    statut = models.CharField(max_length=20, choices=[
        ('reçue', 'Reçue'),
        ('en_cours', 'En cours de traitement'),
        ('rejetée', 'Rejetée'),
        ('acceptée', 'Acceptée')
    ], default='reçue', verbose_name="Statut")

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"

    def __str__(self):
        return f"Candidature de {self.nom} {self.prenom} pour {self.offre.titre}"
# Les Entretiens
class Entretien(models.Model):
    candidature = models.ForeignKey(Candidature, on_delete=models.CASCADE, related_name='entretiens', verbose_name="Candidature")
    date_entretien = models.DateField(verbose_name="Date de l'entretien")
    heure_entretien = models.TimeField(verbose_name="Heure de l'entretien")
    lieu = models.CharField(max_length=255, verbose_name="Lieu de l'entretien")
    commentaires = models.TextField(blank=True, verbose_name="Commentaires")

    class Meta:
        verbose_name = "Entretien"
        verbose_name_plural = "Entretiens"

    def __str__(self):
        return f"Entretien pour {self.candidature.offre.titre} avec {self.candidature.candidat.username} le {self.date_entretien} à {self.heure_entretien}"
    
# Event 
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.title

# Les Messages
User  = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} from {self.sender} to {self.recipient}"
    
# Notification
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"


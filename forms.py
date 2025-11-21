from datetime import  time, date
from .utils import  timezone
from django import forms
from django.contrib.auth.models import User
from .models import (
    Absence, Candidature, Employe, Entretien, Message, OffreEmploi, Retard, Service, Conge, Contrat, Salaire, Event,
    Recrutement, Evaluation, FicheEmploye, SoldeConge, TypeConge, Profile, AvanceSalaire, FichePaie, Prime, TypeContrat, ArchiveContrat
)


# Formulaire pour l'inscription de l'utilisateur
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    company_name = forms.CharField(max_length=255, label="Nom de la société")
    employee_id = forms.CharField(max_length=10, label="ID de l'employé")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'company_name', 'employee_id']
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
        user.set_password(self.cleaned_data['password'])  # Hash le mot de passe
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                employee_id=self.cleaned_data['employee_id']
            )
        return user


# Formulaire pour l'employé
class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['nom', 'prenom', 'sexe', 'date_naissance', 'adresse', 'date_embauche', 'service', 'salaire_base', 'type_contrat']
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'sexe': 'Sexe',
            'date_naissance': 'Date de naissance',
            'adresse': 'Adresse',
            'date_embauche': 'Date d\'embauche',
            'service': 'Service',
            'salaire_base': 'Salaire de base',
            'type_contrat': 'Type de contrat',
        }
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date'}),
            'salaire_base': forms.NumberInput(attrs={'step': '0.01'}), 
        }

    def clean(self):
        cleaned_data = super().clean()
        date_naissance = cleaned_data.get("date_naissance")
        date_embauche = cleaned_data.get("date_embauche")

        if date_naissance and date_naissance > timezone.now().date():
            raise forms.ValidationError("La date de naissance ne peut pas être dans le futur.")

        if date_embauche and date_embauche > timezone.now().date():
            raise forms.ValidationError("La date d'embauche ne peut pas être dans le futur.")

# Formulaire pour le service
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nom', 'description', 'responsable',]
        labels = {
            'nom': 'Nom du service',
            'description': 'Description',
            'responsable': 'Responsable',
        }
# Formulaire pour le congé
class CongeForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = ['employe', 'type_conge', 'date_debut', 'date_fin',]
        labels = {
            'employe': 'Employé',
            'type_conge': 'Type de Congé',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
        }
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  

        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            # verifier le groupe de l'utilisateur
            if user.groups.filter(name='Utilisateurs').exists():
                try:
                    self.fields['employe'].queryset = Employe.objects.filter(email=user.username)
                except AttributeError:
                    self.fields['employe'].queryset = Employe.objects.none()  # l'employe n'existe pas
            # verifier si l'utilisateur est un responsable RH
            elif user.is_staff or user.groups.filter(name='Responsable_RH').exists():
                self.fields['employe'].queryset = Employe.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")

        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")
        
# Formulaire pour le contrat
class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = ['employe', 'type_contrat', 'date_debut', 'date_fin', 'periode_essai', 'renouvellement']
        labels = {
            'employe': 'Employé',
            'type_contrat': 'Type de contrat',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin',
            'periode_essai': 'Période d\'essai (en jours)',
            'renouvellement': 'Renouvellement',
        }
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")

        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")

# Formulaire pour le salaire
class SalaireForm(forms.ModelForm):
    heures_supplementaires = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, label="Heures supplémentaires", required=False)
    primes = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, label="Primes", required=False)

    class Meta:
        model = Salaire
        fields = ['employe', 'date_paiement', 'salaire_base', 'heures_supplementaires', 'primes']
        labels = {
            'employe': 'Employé',
            'date_paiement': 'Date de paiement',
            'salaire_base': 'Salaire de base',
        }
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulaire pour le recrutement
class RecrutementForm(forms.ModelForm):
    class Meta:
        model = Recrutement
        fields = ['employe', 'date_recrutement', 'poste', 'statut']
        labels = {
            'employe': 'Employé',
            'date_recrutement': 'Date de recrutement',
            'poste': 'Poste',
            'statut': 'Statut',
        }
        widgets = {
            'date_recrutement': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulaire pour l'évaluation
class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['employe', 'date_evaluation', 'objectifs_atteints', 'competences_developpees', 'note', 'criteres']
        labels = {
            'employe': 'Employé',
            'date_evaluation': 'Date de l\'évaluation',
            'objectifs_atteints': 'Objectifs atteints',
            'competences_developpees': 'Compétences développées',
            'note': 'Note',
            'criteres': 'Critères d\'évaluation',
        }
        widgets = {
            'date_evaluation': forms.DateInput(attrs={'type': 'date'}),
        }
# Formulaire pour la fiche d'employé
class FicheEmployeForm(forms.ModelForm):
    class Meta:
        model = FicheEmploye
        fields = ['employe', 'competences', 'formations', 'historique_professionnel']
        labels = {
            'employe': 'Employé',
            'competences': 'Compétences',
            'formations': 'Formations',
            'historique_professionnel': 'Historique Professionnel',
        }

# Formulaire pour le type de congé
class TypeCongeForm(forms.ModelForm):
    class Meta:
        model = TypeConge
        fields = ['code', 'description', 'jours_par_an']
        labels = {
            'code': 'Code du type de congé',
            'description': 'Description',
            'jours_par_an': 'Jours par an',
        }
# Formulaire pour solde de congé 
class SoldeCongeForm(forms.ModelForm):
    class Meta:
        model = SoldeConge
        fields = ['employe', 'type_conge', 'solde_initial', 'solde_utilise']
        widgets = {
            'employe': forms.Select(attrs={'class': 'form-select'}),
            'type_conge': forms.Select(attrs={'class': 'form-select'}),
            'solde_initial': forms.NumberInput(attrs={'class': 'form-control'}),
            'solde_utilise': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Formulaire pour demander une avance
class DemanderAvanceForm(forms.Form):
    montant = forms.DecimalField(label="Montant de l'avance", max_digits=10, decimal_places=2)
    justification = forms.CharField(widget=forms.Textarea, label="Justification", max_length=500)

# Formulaire pour la fiche de paie
class FichePaieForm(forms.ModelForm):
    date_paiement = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date de paiement")
    salaire_base = forms.DecimalField(label="Salaire de base", max_digits=10, decimal_places=2)
    salaire_final = forms.DecimalField(label="Salaire final", max_digits=10, decimal_places=2)

    class Meta:
        model = FichePaie
        fields = ['employe', 'date_paiement', 'salaire_base', 'salaire_final']
        labels = {
            'employe': 'Employé',
        }

# Formulaire pour l'avance de salaire
class AvanceSalaireForm(forms.ModelForm):
    class Meta:
        model = AvanceSalaire
        fields = ['employe', 'montant', 'justification', 'date_demande']
        labels = {
            'employe': 'Employé',
            'montant': 'Montant',
            'justification': 'Justification',
            'date_demande': 'Date de demande',
        }
        widgets = {
            'date_demande': forms.DateInput(attrs={'type': 'date'}),
        }

# Formulaire pour la prime
class PrimeForm(forms.ModelForm):
    class Meta:
        model = Prime
        fields = ['employe', 'montant', 'date_attribution', 'description']
        labels = {
            'employe': 'Employé',
            'montant': 'Montant',
            'date_attribution': 'Date d\'attribution',
            'description': 'Description',
        }
        widgets = {
            'date_attribution': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        montant = cleaned_data.get("montant")

        if montant is not None and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")

# Formulaire pour le type de contrat
class TypeContratForm(forms.ModelForm):
    class Meta:
        model = TypeContrat  
        fields = ['code', 'nom', 'description']  
        labels = {
            'code': 'Code du type de contrat',
            'nom': 'Nom du type de contrat',  
            'description': 'Description',
        }

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code")

        if not code:
            raise forms.ValidationError("Le code du type de contrat est requis.")

# Formulaire pour offre d'emploi
class OffreEmploiForm(forms.ModelForm):
    class Meta:
        model = OffreEmploi
        fields = ['titre', 'description', 'date_expiration']
        labels = {
            'titre': 'Titre de l\'offre',
            'description': 'Description',
            'date_expiration': 'Date d\'expiration',
        }

# Formulaire pour les condidateures
class CandidatureForm(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ['nom', 'prenom', 'email', 'cv', 'statut']
        labels = {
            'nom': 'Nom',  
            'prenom': 'Prénom',  
            'email': 'Email',  
            'cv': 'CV',
            'statut':'Statut'  
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}), 
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),  
            'email': forms.EmailInput(attrs={'class': 'form-control'}),  
            'cv': forms.FileInput(attrs={'class': 'form-control'}), 
        }

# Formulaire pour les Entretiens
class EntretienForm(forms.ModelForm):
    class Meta:
        model = Entretien
        fields = ['candidature', 'date_entretien', 'heure_entretien', 'lieu', 'commentaires']
        labels = {
            'candidature': 'Candidature',
            'date_entretien': 'Date de l\'entretien',
            'heure_entretien': 'Heure de l\'entretien',
            'lieu': 'Lieu de l\'entretien',
            'commentaires': 'Commentaires',
        }
        widgets = {
            'candidature': forms.Select(attrs={'class': 'form-control'}),
            'date_entretien': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_entretien': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_date_entretien(self):
        date_entretien = self.cleaned_data.get('date_entretien')
        if date_entretien < date.today():  
            raise forms.ValidationError("La date de l'entretien ne peut pas être dans le passé.")
        return date_entretien

    def clean_heure_entretien(self):
        heure_entretien = self.cleaned_data.get('heure_entretien')
        if heure_entretien < time(8, 0) or heure_entretien > time(15, 0):
            raise forms.ValidationError("L'heure de l'entretien doit être entre 08:00 et 15:00.")
        return heure_entretien
    
# Formulaire pour les Absences 
class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ['employe', 'date_absence', 'justification', 'justificatif']  
        widgets = {
            'date_absence': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super(AbsenceForm, self).__init__(*args, **kwargs)
# Formulaire pour les Retards
class RetardForm(forms.ModelForm):
    class Meta:
        model = Retard
        fields = ['employe', 'date_retard', 'heures_retard', 'justification', 'justificatif']  
        widgets = {
            'date_retard': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RetardForm, self).__init__(*args, **kwargs)
        if user:
            self.instance.employe = user.employe  

        
# Formulaire pour Contact 
class ContactForm(forms.Form):
    name = forms.CharField(label='Nom', max_length=50)
    prenom = forms.CharField(label='Prénom', max_length=50)
    email = forms.EmailField(label='Email')
    message = forms.CharField(label='Message', widget=forms.Textarea)

# Fromulaire for event
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

# Formulaire pour les Messages 
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
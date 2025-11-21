from rest_framework import serializers
from .models import (
    Employe, Conge, Contrat,  FichePaie, Salaire, Recrutement, Evaluation, FicheEmploye, TypeConge, Prime, ArchiveContrat, OffreEmploi, Candidature, Entretien
)

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ['id', 'nom', 'prenom', 'sexe', 'date_naissance', 'date_embauche']

class CongeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conge
        fields = ['id', 'employe', 'type_conge', 'date_debut', 'date_fin', 'statut']

class ContratSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrat
        fields = ['id', 'employe', 'type_contrat', 'date_debut', 'date_fin', 'periode_essai', 'renouvellement']

class SalaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salaire
        fields = ['id', 'employe', 'montant', 'date_paiement']

class RecrutementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recrutement
        fields = ['id', 'offre', 'candidat', 'date_recrutement', 'statut']

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ['id', 'employe', 'score', 'date_evaluation']

class FicheEmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FicheEmploye
        fields = ['id', 'employe', 'date_creation', 'details']

class TypeCongeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeConge
        fields = ['id', 'nom', 'description']

class FichePaieSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichePaie
        fields = ['id', 'employe', 'date_paiement', 'salaire_base', 'salaire_final']

class PrimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prime
        fields = ['id', 'employe', 'montant', 'date_attribution']

class ArchiveContratSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchiveContrat
        fields = ['id', 'contrat', 'date_archivage']

class OffreEmploiSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffreEmploi
        fields = ['id', 'titre', 'description', 'date_publication', 'statut']

class CandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = ['id', 'candidat', 'offre', 'date_candidature', 'statut']

class EntretienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entretien
        fields = ['id', 'candidature', 'date_entretien', 'heure_entretien', 'lieu', 'statut']



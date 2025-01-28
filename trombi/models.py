from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


# Modèle Utilisateur
class Utilisateur(AbstractUser):
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=20,blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True)
    date_naissance = models.DateField(null=True, verbose_name="Année de début")

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",  # Nom unique
        blank=True,
        help_text="Les groupes auxquels cet utilisateur appartient.",
        verbose_name="groupes",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # Nom unique
        blank=True,
        help_text="Les permissions spécifiques à cet utilisateur.",
        verbose_name="permissions de l’utilisateur",
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'


# Modèle de profil utilisateur
class Profile(models.Model):
    school = models.CharField(max_length=200)
    user = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)


# Modèle Template
class Template(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    html_template = models.CharField(max_length=255)  # Nom du fichier HTML
    css_template = models.CharField(max_length=255, blank=True, null=True)  # Nom du fichier CSS (facultatif)
    
    def __str__(self):
        return self.nom

# Modèle CV
class CV(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='user_cvs')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_modification = models.DateTimeField(auto_now=True)

    langues = models.ManyToManyField("Langue", related_name="cv_langues", blank=True)
    competences = models.ManyToManyField("Competence", related_name="cv_competences", blank=True)
    cv_experiences = models.ManyToManyField("Experience", related_name="cv_experiences", blank=True)
    cv_formations = models.ManyToManyField("Formation", related_name="cv_formations", blank=True)

    class Meta:
        verbose_name = 'CV'
        verbose_name_plural = 'CVs'

    def __str__(self):
        return self.titre


# Modèle Expérience
class Experience(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='user_experiences')
    cv = models.ManyToManyField(CV, related_name='experiences_cv', blank=True)
    poste = models.CharField(max_length=200)
    entreprise = models.CharField(max_length=200)
    annee_debut_exp = models.DateField(null=True, verbose_name="Année de début")
    annee_fin_exp = models.DateField(null=True, verbose_name="Année de début")
    description = models.TextField()

    def clean(self):
        if self.annee_fin_exp and self.annee_debut_exp > self.annee_fin:
            raise ValueError("La date de début ne peut pas être postérieure à la date de fin.")

    class Meta:
        verbose_name = 'Expérience'
        verbose_name_plural = 'Expériences'
        ordering = ['-annee_debut_exp']


# Modèle Formation
class Formation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='user_formations')
    cv = models.ManyToManyField(CV, related_name='formations_cv', blank=True)
    diplome = models.CharField(max_length=200)
    etablissement = models.CharField(max_length=200)
    annee_debut_educ = models.IntegerField(null=True, verbose_name="Année de début")
    annee_fin_educ = models.IntegerField(null=True, verbose_name="Année de début")
    description = models.TextField(blank=True)

    def clean(self):
        if self.annee_fin_educ and self.annee_debut_educ > self.annee_fin_educ:
            raise ValueError("La date de début ne peut pas être postérieure à la date de fin.")

    class Meta:
        verbose_name = 'Formation'
        verbose_name_plural = 'Formations'
        ordering = ['-annee_debut_educ']


# Modèle Compétence
class Competence(models.Model):
    NIVEAUX_CECRL = [
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
    ]    

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='user_competences')
    cv = models.ManyToManyField(CV, related_name='competences_cv', blank=True)
    libelle = models.CharField(max_length=100)
    niveau = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'
        unique_together = ['utilisateur', 'libelle']


# Modèle Langue
class Langue(models.Model):
    NIVEAUX_CECRL = [
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
    ]  

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='user_langues')
    cv = models.ManyToManyField(CV, related_name='langues_cv', blank=True)
    libelle = models.CharField(max_length=50)
    niveau = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Langue'
        verbose_name_plural = 'Langues'
        unique_together = ['utilisateur', 'libelle']


# Modèle Projet
class Projet(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='user_projets')
    cv = models.ManyToManyField(CV, related_name='projets_cv', blank=True)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    annee_debut_exp = models.DateField(null=True, verbose_name="Année de début")
    annee_fin_exp = models.DateField(null=True, verbose_name="Année de début")

    def clean(self):
        if self.annee_fin_exp and self.annee_debut_exp > self.annee_fin_exp:
            raise ValueError("La date de début ne peut pas être postérieure à la date de fin.")

    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['-annee_debut_exp']


# Modèle Groupe
class Groupe(models.Model):
    nom = models.CharField(max_length=100)
    admin = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='admin_groupes')
    membres = models.ManyToManyField(Utilisateur, related_name='user_groupes')

    class Meta:
        verbose_name = 'Groupe'
        verbose_name_plural = 'Groupes'

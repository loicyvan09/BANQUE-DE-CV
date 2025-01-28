from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import EmailMessage
from .forms import EmailCVForm
from trombi.models import *
from django.contrib.auth import get_user_model
from datetime import datetime
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.template.loader import get_template
from django.templatetags.static import static
from weasyprint import HTML, CSS
from django.template.loader import render_to_string


def connexion(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Vérification si l'email est fourni
        if not email or not password:
            messages.error(request, "Veuillez fournir un email et un mot de passe.")
            return render(request, 'trombi/login.html')

        # Vérification de l'existence de l'utilisateur
        user = get_user_model().objects.filter(email=email).first()
        if not user:
            messages.error(request, "Aucun utilisateur trouvé avec cet email.")
            return render(request, 'trombi/login.html')

        # Authentification
        auth_user = authenticate(request, username=user.username, password=password)
        if auth_user:
            login(request, auth_user)
            return redirect('cv')
        else:
            messages.error(request, "Mot de passe incorrect.")
            return render(request, 'trombi/login.html')

    return render(request, 'trombi/login.html')

def inscription(request) : 
    error = False
    message = ""
    if request.method == "POST":
        nom = request.POST.get('nom', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
        last_name = request.POST.get('prenom',None)
        first_name = request.POST.get('nom',None)
        telephone = request.POST.get('contact',None)
        photo = request.FILES.get('photo')
        try:
            validate_email(email)
        except:
            error = True
            message = "Entrez un email valide SVP"

        if error == False:
            if password != repassword:
                error = True
                message = "Les deux mots de passe ne sont pas pareils"

        user = get_user_model().objects.filter(Q(email=email) | Q(username=nom)).first()
        if user:
            error = True
            message = f"Un utilisateur a déjà cet Email {email} ou le nom d'utilisateur {nom}"

        if error == False:
            user = get_user_model()(
                username=nom,
                email=email,
                last_name=last_name,
                first_name=first_name,
                telephone = telephone,
                photo = photo
            )

            # Hashing le mot de passe
            user.set_password(password)
            user.save()

            # Optionnel : Si vous avez un modèle de profil utilisateur, vous pouvez le créer ici.
            return redirect('connexion')

    context = {
        'error': error,
        'message': message
    }
    return render(request, 'trombi/inscription.html', context)

@login_required(login_url='connexion')
def dashboard(request) :
    return render(request, 'trombi/dashboard.html')

def deconnexion(request) :
    logout(request)
    return redirect('trombi')

# @login_required(login_url='connexion')
def trombi(request):
   
    utilisateurs = Utilisateur.objects.all()  # Récupère tous les utilisateurs
    return render(request, 'trombi/trombi.html', {'utilisateurs': utilisateurs})

def profile(request,id) :
    utilisateur = get_object_or_404(Utilisateur, id=id)
    return render(request,'trombi/profile.html',{'utilisateur': utilisateur})

@login_required  # Redirige vers la page de connexion si l'utilisateur n'est pas authentifié
def cv(request):
    utilisateur = request.user  # Récupérer l'utilisateur connecté
    cvs = CV.objects.filter(utilisateur=utilisateur)  # Récupérer tous ses CV
    return render(request, 'trombi/cv.html', {'cvs': cvs,'utilisateur':utilisateur})
def info(request):
    # Assurez-vous que 'utilisateur' est bien l'utilisateur connecté
    utilisateur = request.user  # Si vous utilisez l'utilisateur connecté
    return render(request, 'trombi/info.html', {'utilisateur': utilisateur})

@login_required
def add_info(request):
    utilisateur = request.user
    if request.method == "POST":
       # Utilisateur actuellement connecté
        
        # Création du CV
        

        # Enregistrement des langues
        langues = request.POST.getlist("libelle_langue[]")
        niveaux_langues = request.POST.getlist("niveau_langue[]")
        for libelle, niveau in zip(langues, niveaux_langues):
            if libelle and niveau:
                Langue.objects.create(
                    utilisateur=utilisateur,  
                    libelle=libelle, 
                    niveau=niveau)

        # Enregistrement des formations
        diplomes = request.POST.getlist("diplome[]")
        etablissements = request.POST.getlist("etablissement[]")
        annees_debut_educ = request.POST.getlist("annee_debut_educ[]")
        annees_fin_educ = request.POST.getlist("annee_fin_educ[]")

        for diplome, etablissement, debut, fin in zip(diplomes, etablissements, annees_debut_educ, annees_fin_educ):
            if diplome and etablissement and debut:
                if not fin:  # Si la date de fin est vide, on la définit à None
                    fin = None
                else:
                    # Validation que la date de fin n'est pas avant la date de début
                    if fin < debut:
                        messages.error(request, "La date de fin ne peut pas être antérieure à la date de début pour la formation.")
                        return render(request, 'trombi/info.html')
                
                Formation.objects.create(
                    utilisateur=utilisateur,
                    diplome=diplome, 
                    etablissement=etablissement, 
                    annee_debut_educ=debut,
                    annee_fin_educ=fin)

        # Enregistrement des expériences
        postes = request.POST.getlist("poste[]")
        entreprises = request.POST.getlist("entreprise[]")
        annee_debut_exp = request.POST.getlist("annee_debut_exp[]")
        annee_fin_exp = request.POST.getlist("annee_fin_exp[]")

        for poste, entreprise, debut, fin in zip(postes, entreprises, annee_debut_exp, annee_fin_exp):
            if poste and entreprise and debut:
                if not fin:  # Si la date de fin est vide, on la définit à None
                    fin = None
                else:
                    # Validation que la date de fin n'est pas avant la date de début
                    if datetime.strptime(fin, '%Y-%m-%d').date() < datetime.strptime(debut, '%Y-%m-%d').date():
                        messages.error(request, "La date de fin ne peut pas être antérieure à la date de début pour l'expérience.")
                        return render(request, 'trombi/info.html')
                
                Experience.objects.create(
                    utilisateur=utilisateur,  
                    poste=poste, 
                    entreprise=entreprise, 
                    annee_debut_exp=datetime.strptime(debut, '%Y-%m-%d').date() if debut else None, 
                    annee_fin_exp=datetime.strptime(fin, '%Y-%m-%d').date() if fin else None,)

        # Enregistrement des compétences
        competences = request.POST.getlist("competence[]")
        niveaux_competences = request.POST.getlist("niveau_competence[]")
        for competence, niveau in zip(competences, niveaux_competences):
            if competence and niveau:
                Competence.objects.create(
                    utilisateur=utilisateur,  
                    libelle=competence, 
                    niveau=niveau)

        messages.success(request, "Vos Informations ont été enregistrées avec succès !")
        return redirect("info")  # Redirection vers le tableau de bord ou la page de CV

    return render(request, 'trombi/info.html')

def new_cv(request,id):
   
    return redirect('cv')

@login_required
def creer_cv(request):
    utilisateur = request.user

    # Récupérer les données associées à l'utilisateur (indépendamment de GET ou POST)
    langues = Langue.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []
    competences = Competence.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []
    experiences = Experience.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []
    formations = Formation.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []

    return render(request, "trombi/cv1.html", {
        'langues': langues,
        'competences': competences,
        'experiences': experiences,
        'formations': formations,
    })

@login_required
def generer_cv(request):
    utilisateur = request.user
    apropos = ""
    poste = ""

    print(request.POST)
    # Récupérer un CV existant si `cv_id` est fourni
    
    if request.method == "POST":
        # Récupérer les champs du formulaire
        titre = request.POST.get("titre", "Mon CV")
        description = request.POST.get("description", "")
        apropos = request.POST.get("apropo", "")
        poste = request.POST.get("poste", "")

       
            # Créer un nouveau CV
        cv = CV.objects.create(utilisateur=utilisateur, titre=titre, description=description)
                    
                    
        # Récupérer les informations sélectionnées
        langues = Langue.objects.filter(id__in=request.POST.getlist("langues"))
        competences = Competence.objects.filter(id__in=request.POST.getlist("competences"))
        experiences = Experience.objects.filter(id__in=request.POST.getlist("experiences"))
        formations = Formation.objects.filter(id__in=request.POST.getlist("formations"))

        # Mettre à jour les relations ManyToMany seulement si `cv` existe
        if cv:
            cv.langues.set(langues)
            cv.competences.set(competences)
            cv.cv_experiences.set(experiences)
            cv.cv_formations.set(formations)
            cv.save()

        # ✅ Redirection vers la page du CV nouvellement créé
        return redirect('cv')
@login_required
def creation_cv (request, id):
    cv = CV.objects.get(id=id)
    utilisateur = request.user
    # ✅ Affichage du CV existant ou d’un nouveau CV
    langues = cv.langues.all() if cv else []
    competences = cv.competences.all() if cv else []
    experiences = cv.cv_experiences.all() if cv else []
    formations = cv.cv_formations.all() if cv else []
    titre_cv = cv.titre if cv else "Mon CV"

    

    return render(request, "trombi/generer_cv.html", {
        "cv": cv,
        "utilisateur": utilisateur,
        "langues": langues,
        "competences": competences,
        "experiences": experiences,
        "formations": formations,
        "titre_cv": titre_cv,
        # "apropos": apropos,
        # "poste": poste
    })

@login_required
def manage_cv(request, cv_id, action):
    cv = get_object_or_404(CV, id=cv_id)
    utilisateur = request.user
    # Vérifier si l'utilisateur est propriétaire du CV
    if cv.utilisateur != request.user:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à ce CV.")

    if action == "edit":
        cv = CV.objects.get(id=cv.id)
        langues = Langue.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []
        competences = Competence.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []
        experiences = Experience.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []
        formations = Formation.objects.filter(utilisateur=utilisateur) if utilisateur.is_authenticated else []

        # ✅ Affichage du CV existant ou d’un nouveau CV
        langues_all = cv.langues.all() if cv else []
        competences_all = cv.competences.all() if cv else []
        experiences_all = cv.cv_experiences.all() if cv else []
        formations_all = cv.cv_formations.all() if cv else []
        titre_cv = cv.titre if cv else "Mon CV"        
        
       
        return render(request, "trombi/dashboard.html", {
            "cv": cv,
            "langues_all": langues_all,
            "competences_all": competences_all,
            "experiences_all":experiences_all,
            "formations_all": formations_all,
            "langues": langues,
            "competences": competences,
            "experiences":experiences,
            "formations": formations,
        })

    elif action == "delete":
        cv.delete()
        return redirect("cv")

    elif action == "download":
        # Charger le même template que celui utilisé pour l'affichage du CV
        template = get_template("trombi/generer_cv.html")  
        
        # Charger les données du CV
        context = {
            "cv": cv,
            "utilisateur": request.user,
            "langues": cv.langues.all(),
            "competences": cv.competences.all(),
            "experiences": cv.cv_experiences.all(),
            "formations": cv.cv_formations.all(),
            "titre_cv": cv.titre,
        }

        # Générer le contenu HTML
        html_content = template.render(context)

        css_url = request.build_absolute_uri(static('css/cv.css'))
        css = CSS(css_url)


        # Générer le PDF avec WeasyPrint
        pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

        # Créer la réponse HTTP avec le PDF en pièce jointe
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{cv.titre}.pdf"'
        return response

    else:
        return HttpResponse("Action non valide", status=400)
    

def update_cv(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id, utilisateur=request.user)

    if request.method == "POST":
        # Mise à jour des champs texte du CV
        cv.titre = request.POST.get("titre", cv.titre)
        cv.description = request.POST.get("description", cv.description)

        # Mise à jour des relations ManyToMany
        cv.langues.set(Langue.objects.filter(id__in=request.POST.getlist("langues")))
        cv.competences.set(Competence.objects.filter(id__in=request.POST.getlist("competences")))
        cv.cv_experiences.set(Experience.objects.filter(id__in=request.POST.getlist("experiences")))
        cv.cv_formations.set(Formation.objects.filter(id__in=request.POST.getlist("formations")))

        # Sauvegarde du CV mis à jour
        cv.save()

        # Rediriger vers la page d'affichage du CV
        return redirect("new_cv", id=cv.id)

    # Si ce n'est pas une requête POST, on refuse l'accès
    return HttpResponseForbidden("Méthode non autorisée.")


def send_cv_by_email(request, cv_id):
    cv = get_object_or_404(CV, id=cv_id)
    utilisateur = request.user

    # Vérifier si l'utilisateur est propriétaire du CV
    if cv.utilisateur != request.user:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'envoyer ce CV.")

    # Si le formulaire est soumis
    if request.method == "POST":
        form = EmailCVForm(request.POST)
        if form.is_valid():
            email_destinataire = form.cleaned_data["email_destinataire"]
            sujet = form.cleaned_data["sujet"]
            message = form.cleaned_data["message"]

            # Charger le même template que celui utilisé pour l'affichage du CV
            template = render_to_string("trombi/generer_cv.html", {
                "cv": cv,
                "utilisateur": request.user,
                "langues": cv.langues.all(),
                "competences": cv.competences.all(),
                "experiences": cv.cv_experiences.all(),
                "formations": cv.cv_formations.all(),
                "titre_cv": cv.titre,
            })

            # Convertir le template en PDF avec WeasyPrint
            css_url = request.build_absolute_uri(static('css/cv.css'))
            css = CSS(css_url)
            pdf_file = HTML(string=template, base_url=request.build_absolute_uri()).write_pdf()

            # Créer l'e-mail avec l'adresse de l'utilisateur connecté
            email_body = message if message else "Veuillez trouver ci-joint votre CV en format PDF."
            email = EmailMessage(
                subject=sujet,
                body=email_body,
                from_email=utilisateur.email,  # Utilisation de l'email de l'utilisateur connecté
                to=[email_destinataire],  # Envoyer à l'adresse fournie par l'utilisateur
            )
            
            # Joindre le fichier PDF
            email.attach(f"{cv.titre}.pdf", pdf_file, 'application/pdf')

            # Envoyer l'e-mail
            email.send()

            # Rediriger l'utilisateur après l'envoi
            return redirect("cv")

    # Si le formulaire n'a pas encore été soumis, afficher le formulaire
    else:
        form = EmailCVForm()

    return render(request, "trombi/send_cv_form.html", {
        "form": form,
        "cv": cv,
    })
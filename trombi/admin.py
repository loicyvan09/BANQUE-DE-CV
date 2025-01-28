from django.contrib import admin
from django.utils.safestring import mark_safe  # pour afficher des aperçus de contenu HTML

from .models import *

# Enregistrement des autres modèles
admin.site.register(Profile)
admin.site.register(Utilisateur)
admin.site.register(Formation)
admin.site.register(Experience)
admin.site.register(CV)
admin.site.register(Competence)
admin.site.register(Langue)

# Classe personnalisée pour l'administration de Template
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'aperçu_html', 'aperçu_css')  # Ajout des aperçus dans la liste
    fields = ('nom', 'description', 'html_template', 'css_template')

    def aperçu_html(self, obj):
        """Affiche un aperçu du template HTML dans l'admin."""
        return mark_safe(obj.html_template[:200])  # Affiche les 200 premiers caractères
    aperçu_html.short_description = 'Aperçu HTML'

    def aperçu_css(self, obj):
        """Affiche un aperçu du code CSS dans l'admin."""
        return mark_safe(f'<style>{obj.css_template[:200]}</style>')  # Affiche les 200 premiers caractères
    aperçu_css.short_description = 'Aperçu CSS'

# Enregistrement du modèle Template avec la classe personnalisée
admin.site.register(Template, TemplateAdmin)

from django.shortcuts import render,redirect
from django.contrib import messages
from clients.models import Panier,Produit
from django.db.models import Sum
import urllib.parse
from .models import Facture
from django.db import transaction
from nsuma.utils import send_invoice_email
from django.utils import timezone


# Create your views here.
def boutique_view(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
        return render(request, 'warning.html')
    CATEGORIES = ['Cosmetique', 'Alimentation', 'Accessoire', 'Apareil']
    type_doc = request.GET.get('type_doc', 'Accessoire')
    if type_doc not in CATEGORIES:
        type_doc = 'Accessoire'
        
    user = request.user
    panier = None
    if user.is_authenticated:
        panier = Panier.objects.filter(client=user).first()
    produits = Produit.objects.filter(categorie=type_doc)
    context = {
        "produits": produits,
        "panier": panier,
        "type_doc": type_doc,
        "categories": CATEGORIES,
    }
    return render(request, 'boutique/index.html', context)


def details_produit(request,produit):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html')
    produit = Produit.objects.filter(slug=produit).first()

    similaires = Produit.objects.filter(
        categorie=produit.categorie
    ).exclude(identifiant=produit.identifiant).order_by("?")[:2]

    context = {
        "produit":produit,
        "similaires":similaires
    }
    return render(request,"boutique/details.html",context)


@transaction.atomic
def commande_produit(request, produit_id):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
        return render(request, 'warning.html')
    
    numero_service_client = "2120774975404"
    user = request.user
    if not user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour passer commande.")
        return redirect("clients:login")

    produit = Produit.objects.filter(identifiant=produit_id).first()
    if not produit:
        messages.error(request, "Produit introuvable.")
        return redirect("boutique:boutique")  # ou une autre page

    facture = Facture.objects.create(
        contenue="Facture générée",
    )

    # Générer le lien WhatsApp
    lignes = [
        f"🧾 *FACTURE N° {facture.numero}*",
        f"🛍️ Boutique : Nsuma",
        f"📅 Date : {timezone.now().strftime('%d/%m/%Y')}",
        "🛒 *Produit commandé:*"
    ]
    lignes.append(f"▫️ {produit.titre} - 💰 {produit.prix} MAD x 1")
    lignes.append("────────────────")
    lignes.append(f"💵 *Total : {produit.prix} MAD*")
    lignes.append("😎 Merci pour votre confiance ! 🎉")

    message_whatsapp = "\n".join(lignes)

    texte_encode = urllib.parse.quote(message_whatsapp)
    url_whatsapp = f"https://wa.me/{numero_service_client}?text={texte_encode}"

    return redirect(url_whatsapp)



def delete_view(request,identifiant):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html')
    panier = Panier.objects.filter(identifiant=identifiant).first()
    if panier:  
        panier.delete()
    return redirect("boutique:boutique")

def delete_product_view(request, identifiant, slug):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
        return render(request, 'warning.html')

    panier = Panier.objects.filter(identifiant=identifiant).first()
    if panier:
        produit = panier.produits.filter(slug=slug).first()
        if produit:
            panier.produits.remove(produit)

    if panier and panier.produits.count() > 0:
        return redirect("boutique:panier")
    else:
        panier.delete()
        return redirect("boutique:boutique")


def panier_produit(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html')
    
    user = request.user
    total = 0
    if user.is_authenticated:
        panier = Panier.objects.filter(client=user).first()
        total = panier.produits.aggregate(Sum("prix"))["prix__sum"] or 0

    context = {
        "panier":panier,
        "total":total
    }   
    return render(request,"boutique/panier.html",context)


def ajoute_produit(request, produit):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html')
    user = request.user
    if user.is_authenticated:
        panier, created = Panier.objects.get_or_create(client=user)
        try:
            produit_obj = Produit.objects.get(slug=produit) 
        except Produit.DoesNotExist:
            messages.error(request, "Produit introuvable.")
            return redirect('boutique:boutique')
        panier.produits.add(produit_obj)
        panier.save()
        messages.success(request, f"{produit_obj.titre} ajouté au panier.")
        previous_url = request.META.get("HTTP_REFERER", "/")
        return redirect(previous_url)
    else:
        messages.warning(request, "Vous devez être connecté pour ajouter un produit.")
        return redirect('login')



@transaction.atomic
def send_commande(request):
    numero_service_client = "2120774975404"
    user = request.user

    if not user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour passer commande.")
        return redirect("clients:login")

    panier = Panier.objects.filter(client=user).first()
    if not panier or panier.produits.count() == 0:
        messages.warning(request, "Votre panier est vide.")
        return redirect("boutique:panier")

    # Préparer les produits pour le template
    produits_facture = []
    total = 0
    for produit in panier.produits.all():
        produits_facture.append({
            "titre": produit.titre,
            "prix": produit.prix,
            "quantite": 1
        })
        total += produit.prix

    # Créer la facture dans la base
    facture = Facture.objects.create(
        contenue="Facture générée",
    )

    # Contexte pour le template et PDF
    context = {
        "produits": produits_facture,
        "total": total,
        "numero_facture": facture.numero if hasattr(facture, "numero") else f"FAC-{facture.id}",
        "date": timezone.now().strftime("%d/%m/%Y")
    }

    # Envoyer l'email avec PDF
    send_invoice_email(
        subject=f"Nsuma N° de commande :{context['numero_facture']}",
        message="Veillez trouver le résumé de votre commande ",
        recipient_list=[user.email],
        context=context
    )

    # Générer le lien WhatsApp
    lignes = [
        f"🧾 *FACTURE N° {context['numero_facture']}*",
        f"🛍️ Boutique : Nsuma",
        f"📅 Date : {context['date']}",
        "🛒 *Produits commandés :*"
    ]

    for produit in produits_facture:
        lignes.append(f"▫️ {produit['titre']} - 💰 {produit['prix']} MAD x {produit.get('quantite', 1)}")

    lignes.append("────────────────")
    lignes.append(f"💵 *Total : {total} MAD*")
    lignes.append("😎 Merci pour votre confiance ! 🎉")

    message_whatsapp = "\n".join(lignes)

    texte_encode = urllib.parse.quote(message_whatsapp)
    url_whatsapp = f"https://wa.me/{numero_service_client}?text={texte_encode}"

    return redirect(url_whatsapp)


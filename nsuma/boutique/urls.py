from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

from .views import (
    boutique_view,
    ajoute_produit,
    details_produit,
    commande_produit,
    panier_produit,
    delete_view,
    delete_product_view,
    send_commande)

app_name = "boutique"

urlpatterns = [
    path("",boutique_view,name='boutique'),
    path("login/",include("clients.urls"),name="login"),
    path("ajoute/<str:produit>/", ajoute_produit, name="ajoute"),
    path("details/<str:produit>/", details_produit, name="details"),
    path("commande/<str:produit_id>/", commande_produit, name="commande"),
    path("panier/", panier_produit, name="panier"),
    path("delete/<str:identifiant>/",delete_view,name="delete"),
    path("delete/<str:identifiant>/<str:slug>/", delete_product_view, name="delete_produit"),
    path("commander/", send_commande, name="send_commande"),
   

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
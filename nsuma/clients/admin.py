from django.contrib import admin
from .models import (
    Client,
    Boutique,
    Produit,
    Panier,
    Activation)

# Register your models here.
admin.site.register(Client)
admin.site.register(Boutique)
admin.site.register(Produit)
admin.site.register(Panier)
admin.site.register(Activation)

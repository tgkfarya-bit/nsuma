from django.db import models
from uuid import uuid4
import random
import string

class Facture(models.Model):
    identifiant = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    contenue = models.TextField()
    numero = models.CharField(max_length=8, unique=True, editable=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.BooleanField(default=True)
    MODE_LIVRAISON_CHOICES = [
        ("Domicile", "Domicile"),
        ("Point relais", "Point relais"),
    ]
    mode_livraison = models.CharField(max_length=50, choices=MODE_LIVRAISON_CHOICES)
    MODE_PAIEMENT_CHOICES = [
        ("Mobile Money", "Mobile Money"),
        ("carte", "Carte bancaire"),
    ]
    mode_paiement = models.CharField(max_length=50, choices=MODE_PAIEMENT_CHOICES)

    def generate_facture_number(self):
        lettres_obligatoires = "NSUMA"
        obligatoire = random.choice(lettres_obligatoires)
        autres = random.choices(string.ascii_uppercase + string.digits, k=7)
        position = random.randint(0, 7)
        autres.insert(position, obligatoire)
        return "".join(autres)

    def save(self, *args, **kwargs):
        if not self.numero:
            while True:
                numero_propose = self.generate_facture_number()
                if not Facture.objects.filter(numero=numero_propose).exists():
                    self.numero = numero_propose
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Facture N°:{self.numero}"

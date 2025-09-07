from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import random
from django.core.mail import send_mail
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.utils import timezone

# ========================
# Utilisateur (Client)
# ========================
class Client(AbstractUser):
    telephone = models.CharField(max_length=15,blank=True)
    pass


# ========================
# Boutique
# ========================
class Boutique(models.Model):
    identifiant = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    titre = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    ville = models.CharField(max_length=50)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre


# ========================
# Produit
# ========================
class Produit(models.Model):
    identifiant = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    titre = models.CharField(max_length=100)
    description = models.CharField(max_length=150, blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock = models.PositiveIntegerField(default=0)
    boutique = models.ForeignKey(Boutique, on_delete=models.CASCADE, related_name='produits')
    categorie = models.CharField(choices=[
        ('Cosmetique','Cosmetique'),
        ('Alimentation','Alimentation'),
        ('Accessoire','Accessoire'),
        ('Apareil','Apareil'),
    ])
    quantite = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="produits/", blank=True)
    slug = models.SlugField(unique=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        
        # Compresser l'image si elle est présente
        if self.image:
            img = Image.open(self.image)
            img = img.convert('RGB')
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=100) 
            self.image = ContentFile(img_io.getvalue(), name=self.image.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre



# ========================
# Panier
# ========================
class Panier(models.Model):
    identifiant = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='paniers')
    produits = models.ManyToManyField(Produit, related_name='paniers') 
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return timezone.now() > self.created_at + self.date_creation(hours=24)

    def __str__(self):
        return f"Panier de {self.client.username}"


# ========================
# Activation
# ========================
class Activation(models.Model):
    identifiant = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    code = models.CharField(max_length=4, blank=True)
    client = models.ForeignKey("Client", on_delete=models.CASCADE, related_name='activations')
    statut = models.BooleanField(default=False)

    def generate_unique_code(self):
        while True:
            code = f"{random.randint(1000, 9999)}"
            if not Activation.objects.filter(code=code).exists():
                return code

    def send_activation_email(self):
        """Envoie le code d'activation par email au client"""
        subject = "Votre code d'activation"
        message = f"Votre code d'activation nsuma est : {self.code}"
        recipient_list = [self.client.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)

    def save(self, *args, **kwargs):
        if not self.code and not self.statut:
            self.code = self.generate_unique_code()
            # Envoyer l'email après avoir sauvegardé pour garantir que l'objet existe
            self.send_activation_email()
            self.statut = True
        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.client.username}"

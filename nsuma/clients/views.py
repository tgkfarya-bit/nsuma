from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Client,Activation
from django.contrib.auth import login,logout

# messages.error(request, "Tous les champs sont obligatoires.")
# messages.success(request, "Modifications sauvegardées avec succès.")
# messages.warning(request, "Un résident est déjà inscrit avec ce code.")

def login_view(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html')
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password').lower()
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Email ou mot de passe incorrect")
    return render(request, 'clients/login.html')


def logout_view(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html')
    logout(request)
    return redirect('clients:login')


def register_view(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html') 
    if request.method == "POST":
        email = request.POST.get('email').lower()
        mot_de_passe = request.POST.get('password').lower()
        try:
            client = Client.objects.get(email=email)
            messages.info(request, "Un compte existe déjà avec cet email.")
        except Client.DoesNotExist:
            client = Client(username=email, email=email)
            client.set_password(mot_de_passe)
            client.save()
            activation = Activation(client=client)
            activation.save()
            messages.success(request, "Compte créé avec succès. Un code d'activation a été envoyé par email.")
        return redirect('clients:activation')
    return render(request,'clients/register.html')


def activation_view(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if "mobi" not in user_agent and "android" not in user_agent and "iphone" not in user_agent:
            return render(request,'warning.html')
    if request.method == "POST":
        code1 = request.POST.get('code1')
        code2 = request.POST.get('code2')
        code3 = request.POST.get('code3')
        code4 = request.POST.get('code4')
        code = f"{code1}{code2}{code3}{code4}" 
        try:
            activation = Activation.objects.get(code=code)
        except Activation.DoesNotExist:
            return render(request, 'clients/activation.html', {"error": "Code incorrect"})
        if activation.statut:
            login(request, activation.client)
            return redirect('boutique:boutique') 
    return render(request, 'clients/activation.html')
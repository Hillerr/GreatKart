import accounts
from accounts.models import Account
from django.shortcuts import redirect, render
from .forms import RegistrationForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Verification email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail


# Create your views here.
def register(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                username=username, 
                email=email, 
                password=password)
            user.phone_number = phone_number
            user.save()

            messages.success(request, 'Perfil criado com sucesso')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)
        user = auth.authenticate(email=email, password=password)
        print(user)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')

        else:
            messages.error(request, 'Email ou senha estão incorretos')
            return redirect('login')

    return render(request, 'accounts/login.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.get(email=email).exists():
            user = Account.objects.get(email=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Redefinição de senha'
            mail_message = render_to_string(
                'accounts/reset_password_email.html',
                {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                }
            )
            send_email = EmailMessage(
                subject=mail_subject, 
                body=mail_message, to=[email],
                from_email='rafaelhiller23@gmail.com'
            )
            send_email.send()

            messages.success(request, 'Email para redefinir a senha foi enviado')
            return redirect('login')

        else:
            messages.error(request, f'Conta com email {email} não existe') 
            return redirect(request, 'forgot_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None 

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Por favor, redefina a sua senha')
        return redirect('reset_password')

    else:
        messages.error(request, 'Este link está expirado')
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Senha redefinida com sucesso')
            return redirect('login')
        else:
            messages.error(request, 'As senhas não coicidem')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('home')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


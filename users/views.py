from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import views as auth_views

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, "Your account has been created! Your ar now able to login.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


def password_reset_request(request):

    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                current_site = get_current_site(request)
                for user in associated_users:
                    # subject = 'Password Reset Requested'
                    # email_template_name = 'main/password/password_reset_email.txt'
                    c = {
                        'email': user.email,
                        'domain': current_site.domain,
                        'site_name': current_site.name,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                        }
                    # print('------------**************')
                    # print(c)

                    reset_link = c['protocol'] + '://' + c['domain'] + '/password-reset-confirm/' + c['uid'] + '/' + c['token']
                    # print(reset_link)
                    # http://127.0.0.1:8000/password-reset-confirm/Mg/az4jpn-332d600be33544353f070fc3bbf05a66/
                    # 
                    # {'email': 'akshat@thinkbiz.co.in', 'domain': '127.0.0.1:8000', 'site_name': '127.0.0.1:8000',
                    # 'uid': 'Mg', 'user': <User: Akshat>, 'token': 'az4kcd-e16b970b1b23d9a8441c7445f499a50e',
                    # 'protocol': 'http'}
                    # 
                    # email = render_to_string(email_template_name, c)
                    # try:
                    #     send_mail(subject, email, 'admin@example.com',
                    #               [user.email], fail_silently=False)
                    # except BadHeaderError:
                    #     return HttpResponse('Invalid header found.')
                    return redirect(reset_link)
            else:
                messages.warning(request, "User not Found!!!")
                # return HttpResponse('User Not Found!!!')
    password_reset_form = PasswordResetForm()
    return render(request=request,
                  template_name='users/password_reset.html',
                  context={'password_reset_form': password_reset_form})

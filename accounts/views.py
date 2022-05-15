from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import FormView
from django.contrib.auth.models import User

from .forms import UserRegisterForm, UserLoginForm
from .services import get_action_email, token_generator


class Login(FormView):
    """Ф-я для авторизации пользователя"""
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def get(self, request):
        return render(request, self.template_name, context={'form': self.form_class})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is not None and user.is_active:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    return render(request, self.template_name, context={'form': self.form_class,
                                                                        'message': 'Ваш аккаунт не активирован'})
            else:
                return render(request, self.template_name, context={'form': self.form_class,
                                                                    'message': 'окьпк'})
        else:
            return render(request, self.template_name, context={'form': self.form_class,
                                                                'message': 'Ваш аккаунт не активирован или не существует'})



class Registation(FormView):
    """ф-я для регистрации нового пользователя"""
    form_class = UserRegisterForm
    template_name = 'accounts/registration.html'

    def get(self, request):
        return render(request, self.template_name, context={'form': self.form_class})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_active = True


            users = User.objects.all()
            for user in users:
                if user.email == new_user.email:
                    message = 'Выберите другой email, т. к. данный занят'
                    return render(request, self.template_name, context={'form': form,
                                                                        'message': message})
            new_user.save()
            # get_action_email(request, new_user)
        else:
            return render(request, self.template_name, context={'form': self.form_class, 'message': 'Неверные данные'})

        return redirect('/accounts/login')


def activate_user(request, uid64, token):
    """Ф-я для отправки на почту подтверждения личности"""
    try:
        print(uid64)
        print(urlsafe_base64_decode(uid64))
        uid = force_str(urlsafe_base64_decode(uid64))
        print(uid)
        user = User.objects.get(pk=uid)
    except Exception as e:
        user = None

    if user and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('accounts/login')




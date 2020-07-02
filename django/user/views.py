from django.shortcuts import render
from django.contrib.auth import views as views_auth

class LoginView(views_auth.LoginView):
    template_name='user/login.html'
    redirect_authenticated_user=True

    def get_success_url(self):
        # write your logic here
        if self.request.user.is_superuser:
            return '/admin'
        return '/ledger'


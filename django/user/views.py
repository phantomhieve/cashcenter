from django.shortcuts import render
from django.contrib.auth import views as views_auth
from django.urls import reverse


class LoginView(views_auth.LoginView):
    """Custom login view with role-based redirect."""
    
    template_name = 'user/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirect users based on their role."""
        if self.request.user.is_superuser:
            return reverse('admin:index')
        elif self.request.user.is_staff:
            return reverse('ledger_list')
        else:
            return reverse('ledger_base_list')


from django.contrib.auth.mixins import LoginRequiredMixin


class Security(LoginRequiredMixin):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
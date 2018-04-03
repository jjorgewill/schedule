from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from apps.core import models, forms
from django.utils.translation import ugettext_lazy as _

from apps.core.mixin import Security
from apps.core.utils import generate, date_range
from schedule.settings import EMAIL_HOST_USER


class RouterView(Security, generic.RedirectView):
    pattern_name = 'view_dashboard'

    def get_redirect_url(self, *args, **kwargs):
        profile = self.request.user.profile
        if profile.admin:
            return HttpResponseRedirect(reverse('view_dashboard'))
        elif profile.admin:
            return HttpResponseRedirect(reverse('view_dashboard'))
        else:
            return super().get_redirect_url(*args, **kwargs)


# Event
class CalendarView(Security, generic.CreateView):
    template_name = 'events/form_event.html'
    form_class = forms.EventForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = models.Profile.objects.filter(is_removed=False).exclude(user__is_staff=True).order_by('-id')
        info_profile = []
        today = timezone.now()
        for p in profiles:
            hour = p.get_time_per_month(today)
            before = p.get_time_before_today(today)
            last = p.get_time_after_today(today)
            time_after_today_per_turn = p.get_time_after_today_per_turn(today)
            time_before_today_per_turn = p.get_time_before_today_per_turn(today)
            time_per_month_per_turn = p.get_time_per_month_per_turn(today)
            if hour['duration_hours__sum'] and before['duration_hours__sum']:
                percent = int(float(before['duration_hours__sum']) * float(hour['duration_hours__sum']) / 100)
            else:
                percent = 0
            info_profile.append({'hours': hour['duration_hours__sum'],'minutes':hour['duration_minutes__sum'],
                                 'name':p.user.first_name,'last_name':p.user.last_name,
                                 'color':p.color,
                                 'percent':percent,
                                 'time_after_today_per_turn':time_after_today_per_turn,
                                 'time_before_today_per_turn':time_before_today_per_turn,
                                 'time_per_month_per_turn':time_per_month_per_turn,
                                 'hour_before_day': before['duration_hours__sum'],'minutes':before['duration_minutes__sum'],
                                 'hour_last_day':last['duration_hours__sum'],'minutes':last['duration_minutes__sum'],
                                 })
        context['profiles'] = info_profile
        return context

    def form_valid(self, form):
        obj_event = form.save(commit=False)
        date_start = form.cleaned_data.get('date_start')
        date_end = form.cleaned_data.get('date_end')
        turn = form.cleaned_data.get('turn')
        profile = form.cleaned_data.get('profile')
        next_day = date_start + timedelta(1)
        if next_day != date_end:
            list_event = []
            for day in date_range(date_start, date_end):
                event = models.Event()
                event.date = day
                event.turn = turn
                event.profile = profile
                event.duration_hours = turn.duration_hours
                event.duration_minutes = turn.duration_minutes
                list_event.append(event)
            if list_event:
                models.Event.objects.bulk_create(list_event)
        else:
            event = models.Event()
            event.date = date_start
            event.turn = turn
            event.profile = profile
            event.duration_hours = turn.duration_hours
            event.duration_minutes = turn.duration_minutes
            event.save()
        messages.success(self.request, _('This event has been save'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('create_calendar')


# Turns
class TurnsCreateView(Security, generic.CreateView):
    template_name = 'turns/form_turn.html'
    # permission_required = 'core.can_create_turns'
    form_class = forms.TurnForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        turn = form.save(commit=False)
        hour = form.cleaned_data.get('hour')
        duracion = str(hour.get_amount_time).split(":")
        turn.duration_hours = duracion[0]
        turn.duration_minutes = duracion[1]
        turn.save()
        messages.success(self.request, _('This turn has been save'))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('create_turns')


class TurnsView(Security, generic.ListView):
    template_name = 'turns/view_turn.html'
    model = models.Turn
    context_object_name = 'turns'


class GetTurnsView(Security, generic.ListView):
    template_name = 'turns/view_turn.html'
    model = models.Turn
    context_object_name = 'turns'

    def get(self, request, *args, **kwargs):
        date = request.GET.get('date').split('-')
        year = int(date[1])
        month = int(date[0])
        events = models.Event.objects.filter(date__month=month,
                                             date__year=year, is_removed=False).distinct()
        data = []
        for obj in events:
            abbreviation = obj.profile.profession.abbreviation if obj.profile.profession else ""
            data.append({
                'title': obj.turn.name + " " + abbreviation + " " + obj.profile.user.first_name,
                'start': obj.date.strftime('%Y-%m-%d'),
                'end': obj.date.strftime('%Y-%m-%d'),
                'color': obj.profile.color,
                'profile': obj.profile.id,
                'id': obj.id,
            })
        return JsonResponse({'status': True, 'data': data})


# Profile
class ProfilesCreateView(Security, generic.CreateView):
    template_name = 'profiles/form_profile.html'
    # permission_required = 'core.can_view_clients'
    form_class = forms.ProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context.update({'title': _("Create profile")})
        context.update(
            {'profiles': models.Profile.objects.filter(is_removed=False).exclude(user__is_staff=True).order_by('-id')
            .exclude(id=profile.id)})
        return context

    def form_valid(self, form):
        obj_form = form.save(commit=False)
        email = form.data.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            user = User()
            user.first_name = form.data.get('first_name')
            user.last_name = form.data.get('last_name')
            user.email = email
            user.username = email
            password = generate()
            user.set_password(password)
            user.save()
            # add_permission_customer(user)
            # send_mail('backend/email/create_user.tpl', {'password': password, 'user': email,
            #                                             'accountant': self.request.user.first_name},
            #           EMAIL_HOST_USER, [form.data.get('email')])
            profile = models.Profile.objects.get(user__email=email)
            profile.phone = form.cleaned_data.get('phone')
            profile.profession = form.cleaned_data.get('profession')
            profile.avatar = form.files.get('avatar')
            profile.color = form.cleaned_data.get('color')
            profile.save()
        messages.success(self.request, _('This profile has been save'))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, _('We are sorry, their attributes required your atention'))
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('create_profiles')


class ProfilesUpdateView(Security, generic.UpdateView):
    template_name = 'profiles/form_profile.html'
    model = models.Profile
    # permission_required = 'core.can_view_clients'
    form_class = forms.ProfileForm

    def get_initial(self):
        profile = self.object
        return {
            'first_name': self.object.user.first_name,
            'last_name': self.object.user.last_name,
            'phone': self.object.phone,
            'email': self.object.user.email,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context.update({'title': _("Create profile")})
        context.update(
            {'profiles': models.Profile.objects.filter(is_removed=False).exclude(user__is_staff=True).order_by('-id')
            .exclude(id=profile.id)})
        return context

    def form_valid(self, form):
        obj_form = form.save(commit=False)
        email = form.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            user.first_name = form.data.get('first_name')
            user.last_name = form.data.get('last_name')
            user.email = email
            user.username = email
            user.save()
            profile = models.Profile.objects.get(user__email=email)
            profile.phone = form.cleaned_data.get('phone')
            profile.profession = form.cleaned_data.get('profession')
            profile.avatar = form.files.get('avatar')
            profile.color = form.cleaned_data.get('color')
            profile.save()
        messages.success(self.request, _('This profile has been save'))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, _('We are sorry, their attributes required your atention'))
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('update_profiles', kwargs={'pk': self.kwargs.get('pk')})


class ProfilesView(Security, generic.ListView):
    template_name = 'profiles/view_profile.html'
    model = models.Profile
    context_object_name = 'profiles'

    def get_queryset(self):
        return models.Profile.objects.filter(is_removed=False).exclude(user__is_staff=True).order_by('-id')


#Hour
class HoursCreateView(Security, generic.CreateView):
    template_name = 'hours/form_hour.html'
    # permission_required = 'core.can_view_clients'
    form_class = forms.HourForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('create_holidays')


class HoursView(Security, generic.ListView):
    template_name = 'hours/view_hour.html'
    model = models.Hour
    context_object_name = 'hours'


# Holiday
class HolidaysCreateView(Security, generic.CreateView):
    template_name = 'holidays/form_holiday.html'
    # permission_required = 'core.can_view_clients'
    form_class = forms.HolidayForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('create_holidays')


class HolidaysView(Security, generic.ListView):
    template_name = 'holidays/view_holiday.html'
    model = models.Holiday
    context_object_name = 'holidays'


# Profession
class ProfessionsCreateView(Security, generic.CreateView):
    template_name = 'professions/form_profession.html'
    # permission_required = 'core.can_view_clients'
    form_class = forms.ProfessionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('create_professions')


class ProfessionsView(Security, generic.ListView):
    template_name = 'professions/view_profession.html'
    model = models.Profession
    context_object_name = 'professions'

    def get_queryset(self):
        return models.Profession.objects.filter(is_removed=False).order_by('-id')


# dash
class Dashboard(Security, generic.TemplateView):
    template_name = 'dashboard.html'

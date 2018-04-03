import calendar
import datetime

from django.db.models import Q, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils.models import SoftDeletableModel, TimeStampedModel

from schedule.settings import MEDIA_URL
from django.contrib.auth.models import User, Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str


def get_path_avatar(instance, filename):
    return "upload/{0}/avatar/{1}".format(instance.id, smart_str(filename))


class Profession(TimeStampedModel, SoftDeletableModel):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=10)

    class Meta:
        verbose_name = _("Profession")
        verbose_name_plural = _("Professions")

    def __str__(self):
        return self.name


class Profile(TimeStampedModel, SoftDeletableModel):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)
    admin = models.NullBooleanField()
    avatar = models.FileField(blank=True, null=True, upload_to=get_path_avatar)
    profession = models.ForeignKey(Profession, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        if self.user and self.user.first_name:
            if self.profession:
                return self.profession.abbreviation + ' ' + self.user.first_name
            else:
                return self.user.first_name
        else:
            return str(self.id)

    def get_time_after_today(self,today):
        day = datetime.datetime.now().day
        last_day = calendar.monthrange(today.year,today.month)[1]
        hours_next = self.event_set.filter(date__month=today.month,
                                           date__year=today.year,
                                           date__day__lte=last_day,
                                           date__day__gte=day,
                                           is_removed=False).distinct().aggregate(
            Sum('duration_hours'),Sum('duration_minutes'))
        return hours_next

    def get_time_before_today(self, today):
        day = today.day
        hours_before = self.event_set.filter(date__month=today.month,
                                           date__year=today.year,
                                           date__day__lte=day,
                                           date__day__gte=1,
                                           is_removed=False).distinct().aggregate(
            Sum('duration_hours'),Sum('duration_minutes'))
        return hours_before

    def get_time_per_month(self, today):
        events_hours = self.event_set.filter(date__month=today.month,
                                             date__year=today.year,
                                             is_removed=False).distinct().aggregate(
            Sum('duration_hours'),Sum('duration_minutes'))
        return events_hours

    def get_time_after_today_per_turn(self,today):
        day = datetime.datetime.now().day
        last_day = calendar.monthrange(today.year,today.month)[1]
        hours_next = self.event_set.filter(date__month=today.month,
                                           date__year=today.year,
                                           date__day__lte=last_day,
                                           date__day__gte=day,
                                           is_removed=False).values('turn__name').annotate(
            Sum('duration_hours'),Sum('duration_minutes'))
        return hours_next

    def get_time_before_today_per_turn(self, today):
        day = today.day
        hours_before = self.event_set.filter(date__month=today.month,
                                           date__year=today.year,
                                           date__day__lte=day,
                                           date__day__gte=1,
                                           is_removed=False).values('turn__name').annotate(
            Sum('duration_hours'),Sum('duration_minutes'))
        return hours_before

    def get_time_per_month_per_turn(self, today):
        events_hours = self.event_set.filter(date__month=today.month,
                                             date__year=today.year,
                                             is_removed=False).values('turn__name').annotate(
            Sum('duration_hours'),Sum('duration_minutes'))
        return events_hours

    @property
    def get_avatar(self):
        if not self.avatar:
            return '/static/app/img/no_user.jpg'
        else:
            return MEDIA_URL + str(self.avatar)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            profile = Profile.objects.create(user=instance)
            # can_dashboard = Permission.objects.get(codename='can_dashboard')
            # can_inbox = Permission.objects.get(codename='can_inbox')
            # profile.user.user_permissions.add(can_dashboard)
            # profile.user.user_permissions.add(can_inbox)


class Hour(TimeStampedModel, SoftDeletableModel):
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)

    class Meta:
        verbose_name = _("Hour")
        verbose_name_plural = _("Hours")

    def __str__(self):
        return str(self.start_time)

    @property
    def as_dict(self):
        return {
            'start_time': self.start_time,
            'end_time': self.end_time
        }

    @property
    def get_amount_time(self):
        if self.end_time:
            end = datetime.timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
            start = datetime.timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
            return end - start
        else:
            return 0


class Turn(TimeStampedModel, SoftDeletableModel):
    name = models.CharField(max_length=100)  # noche,tarde,manana
    hour = models.ForeignKey(Hour, blank=True, null=True, on_delete=models.SET_NULL)
    duration_hours = models.IntegerField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("Turn")
        verbose_name_plural = _("Turns")
        ordering = ['hour__start_time']

    def __str__(self):
        return self.name

    @property
    def get_amount_hours(self):
        return self.duration_hours

    @property
    def get_amount_minutes(self):
        return self.duration_minutes


class Status(models.Model):
    name = models.CharField(max_length=100)  # planificado,trabajado

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Statuses")

    def __str__(self):
        return self.name


class Event(TimeStampedModel, SoftDeletableModel):
    date = models.DateField()
    turn = models.ForeignKey(Turn, blank=True, null=True, on_delete=models.SET_NULL)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, blank=True, null=True)  # programed, plaint
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    duration_hours = models.IntegerField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return str(self.date_start) + ' ' + self.profile.user.first_name


class Holiday(TimeStampedModel, SoftDeletableModel):
    day = models.DateField()

    class Meta:
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")

    def __str__(self):
        return str(self.day)


class NonWorkingDay(TimeStampedModel, SoftDeletableModel):
    name = models.CharField(max_length=20)
    number_day = models.IntegerField()

    class Meta:
        verbose_name = _("NonWorkingDay")
        verbose_name_plural = _("NonWorkingDays")

    def __str__(self):
        return self.name


class MotiveAffectation(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name = _("MotiveAffectation")
        verbose_name_plural = _("MotiveAffectations")

    def __str__(self):
        return self.name


class Affectation(TimeStampedModel, SoftDeletableModel):
    hour = models.ForeignKey(Hour, blank=True, null=True, on_delete=models.SET_NULL)
    motive = models.ForeignKey(MotiveAffectation, blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(blank=True, null=True)


class Feature(models.Model):
    menu_item_name = models.CharField(verbose_name=_('Item Name'), max_length=100)
    url = models.CharField(verbose_name=_('Url'), max_length=100)
    icon = models.CharField(verbose_name=_('Icon'), max_length=100)
    position = models.PositiveIntegerField(verbose_name=_('Position'), blank=True, null=True)
    child = models.ForeignKey('self', related_name='child_feature', on_delete=models.SET_NULL, blank=True, null=True)
    permission = models.ManyToManyField(Permission)

    class Meta:
        verbose_name = _("Feature")
        verbose_name_plural = _("Features")

    def __str__(self):
        return self.menu_item_name

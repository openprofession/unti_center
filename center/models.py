from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

STATUS_ALFA = 'alpha'
STATUS_BETA = 'beta'
STATUS_PROD = 'green'
STATUS_CHOICES = (
    (STATUS_ALFA, _('Альфа версия')),
    (STATUS_BETA, _('Бета версия')),
    (STATUS_PROD, _('Продакшн')),
)


class User(AbstractUser):
    second_name = models.CharField(max_length=50)
    is_assistant = models.BooleanField(default=False)
    unti_id = models.IntegerField(null=True, blank=True, unique=True)
    leader_id = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return '%s %s' % (self.unti_id, self.get_full_name)

    @property
    def fio(self):
        return ' '.join(filter(None, [self.last_name, self.first_name, self.second_name]))

    @property
    def get_full_name(self):
        return ' '.join(filter(None, [self.last_name, self.first_name]))


class Dashboard(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = models.ImageField(blank=True)
    public = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    url = models.URLField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_ALFA)
    priority = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Report(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = models.ImageField(blank=True)
    public = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    sql = models.TextField(blank=True)
    source_db = models.CharField(max_length=50, choices=(('dwh', 'DWH Producation'), ('dwh-test', 'DWH Testing')),
                                 default='dwh')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_ALFA)
    priority = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

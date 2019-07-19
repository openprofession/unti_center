from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django import forms


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
    admin = models.BooleanField(default=False)
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


# ############################################################################ #


class ExportFilter(models.Model):
    class Meta:
        verbose_name = _('Фильтр данных')
        verbose_name_plural = _('Фильтра данных')
    #
    name_column = models.CharField(
        verbose_name=_('Название стобца'),
        max_length=255,
        null=False, blank=False,
    )
    name_url_arg = models.CharField(
        verbose_name=_('Название переменной в GET запросе'),
        max_length=255,
        null=False, blank=False,
    )
    name_verbose = models.CharField(
        verbose_name=_('Отображаемое имя фильтра'),
        max_length=255,
        null=False, blank=False,
    )
    placeholder = models.CharField(
        verbose_name=_('подсказка внутри поля ввода'),
        max_length=255,
        null=True, blank=True,
        default='Поле можно оставить пустым...'
    )
    description = models.TextField(
        verbose_name=_('Описание'),
        null=True, blank=True,
    )

    # https://en.wikipedia.org/wiki/Relational_operator
    OPERATOR_EQUAL = '=='
    OPERATOR_NOT_EQUAL = '!='
    OPERATOR_GREATER_THEN = '>'
    OPERATOR_LESS_THEN = '<'
    OPERATOR_GREATER_OR_EQUAL = '>='
    OPERATOR_LESS_OR_EQUAL = '<='

    OPERATOR_CHOICES = (
        (OPERATOR_EQUAL,            OPERATOR_EQUAL),
        (OPERATOR_NOT_EQUAL,        OPERATOR_NOT_EQUAL),
        (OPERATOR_GREATER_THEN,     OPERATOR_GREATER_THEN),
        (OPERATOR_LESS_THEN,        OPERATOR_LESS_THEN),
        (OPERATOR_GREATER_OR_EQUAL, OPERATOR_GREATER_OR_EQUAL),
        (OPERATOR_LESS_OR_EQUAL,    OPERATOR_LESS_OR_EQUAL),
    )

    operator = models.CharField(
        verbose_name=_('оператор сравнения'),
        choices=OPERATOR_CHOICES,
        max_length=255,
        null=False, blank=False,
    )

    is_choices = models.BooleanField(
        verbose_name=_('сформировать choices из базы'),
        default=False,
        null=False, blank=False,
    )

    is_disabled = models.BooleanField(
        verbose_name=_('фильтр выключен'),
        default=False,
        null=False, blank=False,
    )

    DATA_TYPE_STR = 'str'
    DATA_TYPE_INT = 'int'
    DATA_TYPE_DATETIME = 'datetime'
    DATA_TYPE_CHOICE = 'choices'
    DATA_TYPE_CHOICES = (
        (DATA_TYPE_STR,         DATA_TYPE_STR),
        (DATA_TYPE_INT,         DATA_TYPE_INT),
        (DATA_TYPE_DATETIME,    DATA_TYPE_DATETIME),
    )

    data_type = models.CharField(
        verbose_name=_('Тип переменной'),
        choices=DATA_TYPE_CHOICES,
        max_length=255,
        null=False, blank=False,
    )

    def __str__(self):
        if not self.is_choices:
            return '{}(id{}) {} {} {}'.format(
                ['', '(OFF) '][self.is_disabled],
                self.pk,
                self.name_column,
                self.operator,
                self.data_type,
            )
        else:
            return '{}(id{}) {} {} [{},...]'.format(
                ['', '(OFF) '][self.is_disabled],
                self.pk,
                self.name_column,
                self.operator,
                self.data_type,
            )
        #

    def save(self, *args, **kwargs):
        self.name_column = self.name_column.strip()
        self.name_url_arg = self.name_url_arg.strip()
        if self.is_choices:
            self.operator = self.OPERATOR_EQUAL
        #
        return super(ExportFilter, self).save(*args, **kwargs)

    CHOICE_ANY = 'any_choice'


class DataExport(models.Model):
    class Meta:
        verbose_name = _('Эксрорт данных')
        verbose_name_plural = _('Эксрорт данных')
    #
    title = models.CharField(
        verbose_name=_('Заголовок'),
        max_length=255,
        null=False, blank=False,
    )
    description = models.TextField(
        verbose_name=_('Описание'),
        null=True, blank=True,
    )
    sql = models.TextField(
        verbose_name=_('sql запрос к базе'),
        null=False, blank=False,
    )
    filters = models.ManyToManyField(
        ExportFilter,
        verbose_name=_('фильтры данных при экспрте'),
    )

    def get_filters(self):
        return self.filters.filter(is_disabled=False).all()

    is_disabled = models.BooleanField(
        verbose_name=_('экспорт выключен'),
        default=False,
        null=False, blank=False,
    )

    result_file_name = models.CharField(
        verbose_name=_('имя файла для выгрузки'),
        max_length=255,
        null=False, blank=False,
        default='result',
    )

    def __str__(self):
        return '(id{}) {}'.format(
            self.pk,
            self.title,
        )

    def get_form_cls(self, choices_callback):
        # https://simpleisbetterthancomplex.com/tutorial/2018/08/13/how-to-use-bootstrap-4-forms-with-django.html
        _filters = self.get_filters()
        fields = {}
        for fr in _filters:
            field_attrs = {
                'placeholder': fr.placeholder,
            }
            field_kwargs = dict(
                    label=fr.name_verbose,
                    label_suffix='',
                    required=False,
                    help_text=fr.description,
            )
            if fr.is_choices:
                choices = choices_callback(fr.name_column)
                field_kwargs['choices'] = (
                    *choices,
                    (ExportFilter.CHOICE_ANY, _('Все')),
                )
                fields[fr.name_url_arg] = forms.ChoiceField(
                    widget=forms.Select(attrs={
                        'title': fr.placeholder,
                    }),
                    **field_kwargs,
                    initial='',
                )

                continue
            #

            if fr.data_type == fr.DATA_TYPE_STR:
                fields[fr.name_url_arg] = forms.CharField(
                    widget=forms.TextInput(attrs=field_attrs),
                    **field_kwargs,
                )
                continue
            #
            if fr.data_type == fr.DATA_TYPE_INT:
                fields[fr.name_url_arg] = forms.IntegerField(
                    widget=forms.NumberInput(attrs=field_attrs),
                    **field_kwargs,
                )
                continue
            #
            if fr.data_type == fr.DATA_TYPE_DATETIME:
                field_kwargs['help_text'] = '{}, {}'.format(
                    fr.description,
                    'допустимый формат YYYY-mm-dd или YYYY-mm-dd HH:MM'
                )
                fields[fr.name_url_arg] = forms.DateTimeField(
                    widget=forms.DateInput(attrs=field_attrs),
                    input_formats=[
                        '%Y-%m-%d',
                        '%Y-%m-%d %H:%M',
                    ],
                    **field_kwargs,
                )
                continue
            #
            raise RuntimeError('invalid field type')
        #
        return type("FilterForm", (forms.Form,), fields)


# ############################################################################ #

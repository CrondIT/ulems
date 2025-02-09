from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# class for record's created time and updated time


# -----------------------------------------------------------------------------------
class TimeStamp(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name='%(app_label)s_%(class)s_created_related',
        blank=True, on_delete=models.CASCADE, null=True
        )
    updated_by = models.ForeignKey(
        User, related_name='%(app_label)s_%(class)s_updated_related',
        blank=True, on_delete=models.CASCADE, null=True
        )

    class Meta:
        abstract = True


# -----------------------------------------------------------------------------------
def user_directory_path(instance, filename):
    # путь, куда будет осуществлена загрузка MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.created_by.id, filename)


# -----------------------------------------------------------------------------------
class UserImage(TimeStamp):
    title = models.CharField('Название', max_length=200)
    image = models.ImageField(upload_to=user_directory_path, null=True)
    width = models.PositiveSmallIntegerField('Ширина, мм', default=210)
    height = models.PositiveSmallIntegerField('Высота, мм', default=297)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


# -----------------------------------------------------------------------------------
class Event(TimeStamp):
    title = models.CharField('Название', max_length=200,
                             default='Новое мероприятие')
    print_title = models.TextField('Название для печати')
    description = models.TextField('Описание')
    from_date = models.DateField('Дата начала')
    to_date = models.DateField('Дата окончания')
    team_registration = models.BooleanField('Регистрация команды',
                                            default=True)
    image = models.ForeignKey(UserImage,
                              on_delete=models.CASCADE,
                              related_name="event_cover",
                              null=True,
                              blank=True
                              )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


# -----------------------------------------------------------------------------------
class EventRelated(models.Model):

    event_related = models.ForeignKey(
        Event, related_name='%(app_label)s_%(class)s_event_related',
        blank=True, on_delete=models.CASCADE, null=True
        )

    class Meta:
        abstract = True

    
# -----------------------------------------------------------------------------------
class Category(TimeStamp, EventRelated):
    title = models.CharField("Категория участника", max_length=100)
    print_title = models.TextField('Название для печати')
    badge = models.ForeignKey(UserImage,
                              on_delete=models.SET_NULL,
                              related_name="category_badge",
                              null=True,
                              blank=True
                              )
    certificate = models.ForeignKey(UserImage,
                                    on_delete=models.SET_NULL,
                                    related_name="category_certificate",
                                    null=True,
                                    blank=True
                                    )

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Категория участника'
        verbose_name_plural = 'Категории участников'


# -----------------------------------------------------------------------------------
class Competency(TimeStamp, EventRelated):
    title = models.CharField("Компетенция (номинация)", max_length=100)
    print_title = models.TextField('Название для печати')

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Компетенция (номинация)'
        verbose_name_plural = 'Компетенции (номинации)'


# -----------------------------------------------------------------------------------
class Award(TimeStamp, EventRelated):
    title = models.CharField("Награда", max_length=100)
    competency = models.ForeignKey(
        Competency, on_delete=models.SET_NULL,
        related_name="award_competency",
        null=True,
        blank=True
        )
    award = models.ForeignKey(UserImage,
                              on_delete=models.SET_NULL,
                              related_name="award_image",
                              null=True,
                              blank=True
                              )

    def __str__(self):
        return f"{self.title} в {
                self.competency}"

    class Meta:
        verbose_name = 'Награда'
        verbose_name_plural = 'Награды'


# -----------------------------------------------------------------------------------
class Participant(TimeStamp, EventRelated):
    first_name = models.CharField("Фамилия",
                                  max_length=100,
                                  help_text="До 100 символов",
                                  )
    middle_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Отчество", max_length=100)
    organization = models.CharField("Организация", max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name="participants",
        null=True
        )
    competency = models.ForeignKey(
        Competency, on_delete=models.CASCADE,
        related_name="participants",
        null=True
        )
    award = models.ForeignKey(
        Award, on_delete=models.SET_NULL,
        related_name="participant_award",
        null=True,
        blank=True
        )

    def __str__(self):
        return f" {self.first_name} {self.middle_name} {self.last_name} -  {
            self.event_related} {self.category}"

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'


# -----------------------------------------------------------------------------------
class Profile(TimeStamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    current_event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True
        )
    current_image = models.ForeignKey(
        UserImage,
        on_delete=models.SET_NULL,
        null=True
        )
    sort_event = models.CharField(max_length=25,  default="created_date")
    sort_category = models.CharField(max_length=25,  default="created_date")
    sort_competency = models.CharField(max_length=25,  default="created_date")
    sort_award = models.CharField(max_length=25,  default="created_date")
    sort_participant = models.CharField(max_length=25,  default="created_date")
    sort_image = models.CharField(max_length=25, default="created_date")
    sort_template = models.CharField(max_length=25, default="created_date")
  
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return f"Profile: {self.user}"

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


# -----------------------------------------------------------------------------------
class PrintTemplate(TimeStamp):
    print_item = models.CharField(max_length=25, choices=[
        ('event', 'Мероприятие'),
        ('category', 'Категория'),
        ('competency', 'Компетенция (номинация)'),
        ('fio', 'Фамилия Имя Отчество'),
        ('text', 'Текст участника'),
        ('custom_text', 'Произвольный техт')
        ])
    start_x = models.PositiveSmallIntegerField()
    start_y = models.PositiveSmallIntegerField()
    delta_x = models.PositiveSmallIntegerField()
    font_color = models.CharField(max_length=25, null=True)
    font_size = models.PositiveSmallIntegerField()
    user_image_related = models.ForeignKey(
        UserImage, related_name='%(app_label)s_%(class)s_user_image_related',
        blank=True, on_delete=models.CASCADE, null=True
        )

    def __str__(self):
        return f"Шаблон печати: {self.user_image_related} для {
                self.print_item}"

    class Meta:
        verbose_name = 'Шаблон печати'
        verbose_name_plural = 'Шаблоны печати'

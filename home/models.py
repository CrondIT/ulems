from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# class for record's created time and updated time

# -----------------------------------------------------------------------------------
class TimeStamp(models.Model):
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created_related', blank=True, on_delete=models.CASCADE, null=True)
    updated_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_updated_related', blank=True, on_delete=models.CASCADE, null=True)
   
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
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Изображениe'
        verbose_name_plural = 'Изображения'
# -----------------------------------------------------------------------------------
class Event(TimeStamp):
    title = models.CharField('Название', max_length=200, default='Новое мероприятие')
    print_title = models.TextField('Название для печати')
    description = models.TextField('Описание') 
    from_date = models.DateField('Дата начала')
    to_date = models.DateField('Дата окончания')
    cover = models.ImageField(upload_to=user_directory_path, null=True)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

# -----------------------------------------------------------------------------------
class EventRelated(models.Model):

    event_related = models.ForeignKey(Event, related_name='%(app_label)s_%(class)s_event_related', blank=True, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True              

# -----------------------------------------------------------------------------------
class Category(TimeStamp, EventRelated):
   
    title = models.CharField("Категория участника", max_length=100)
    print_title = models.TextField('Название для печати')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Категория участника'
        verbose_name_plural = 'Категории участников'
        # ordering = ['title']
# -----------------------------------------------------------------------------------
class Competency(TimeStamp, EventRelated):
    title = models.CharField("Компетенция (номинация)", max_length=100)
    print_title = models.TextField('Название для печати')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Компетенция (номинация)'
        verbose_name_plural = 'Компетенции (номинации)'

# -----------------------------------------------------------------------------------
class Participant(TimeStamp, EventRelated):
    first_name = models.CharField("Фамилия", max_length=100)
    middle_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Отчество", max_length=100)
    organization = models.CharField("Организация", max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="participants", null=True)
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name="participants", null=True)

    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name} - {self.event} {self.category}"
    
    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

# -----------------------------------------------------------------------------------
class Profile(TimeStamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    current_event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    
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


  
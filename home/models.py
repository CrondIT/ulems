from django.db import models

# class for record's created time and updated time
class TimeStamp(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(TimeStamp):
    title = models.CharField('Название', max_length=200, default='Новое мероприятие')
    print_title = models.TextField('Название для печати')
    description = models.TextField('Описание') 
    from_date = models.DateField('Дата начала')
    to_date = models.DateField('Дата окончания')
   
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

class Person(TimeStamp):
    first_name = models.CharField("Имя", max_length=100)
    middle_name = models.CharField("Фамилия", max_length=100)
    last_name = models.CharField("Отчество", max_length=100)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Физическое лицо'
        verbose_name_plural = 'Физические лица'

class Category(TimeStamp):
    category = models.CharField("Категория участника", max_length=100)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Категория участника'
        verbose_name_plural = 'Категории участников'

class Participant(TimeStamp):
    name = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="pname" )        
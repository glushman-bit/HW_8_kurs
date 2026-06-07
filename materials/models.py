from django.db import models


class Course(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название курса',
        help_text='Укажите название курса',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание курса',
        help_text='Укажите описание курса',
    )
    image = models.ImageField(
        upload_to='courses/images',
        blank=True,
        null=True,
        verbose_name='Превью курса',
        help_text='Загрузите превью',
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название урока',
        help_text='Укажите название урока',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание урока',
        help_text='Введите описание урока',
    )
    image = models.ImageField(
        upload_to='lessons/images',
        blank=True,
        null=True,
        verbose_name='Превью урока',
        help_text='Загрузите превью урока',
    )
    video_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ссылка на урок',
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return self.name

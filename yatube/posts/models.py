from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint, CheckConstraint, Q, F


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Укажите заголовок',
    )
    slug = models.SlugField(
        max_length=200, unique=True,
        verbose_name='ЧПУ',
        help_text='ЧеловекоПонятный УРЛ',
    )
    description = models.TextField(
        verbose_name='Опиcание',
        help_text='Введите описание'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    LEN_OF_POST: int = 15
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Укажите автора',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:self.LEN_OF_POST]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст нового комментария',
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        UniqueConstraint(fields=['user', 'author'], name='unique_follow')
        CheckConstraint(
            check=~Q(user=F('author')),
            name='not_follow_yourselfe'
        )

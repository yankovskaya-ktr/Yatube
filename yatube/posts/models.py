from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='текст',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа',
        help_text='Выберите группу, в которую хотите добавить запись'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Картинка'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='комментарий',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField('date published', auto_now_add=True)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    # Кто подписан
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    # На кого подписан
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            ),
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

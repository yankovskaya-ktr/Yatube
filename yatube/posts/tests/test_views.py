import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post, User


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.MEDIA_ROOT))
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.img = SimpleUploadedFile(
            name='test_img.gif',
            content=test_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(username='John')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание'
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another-group-slug',
            description='Другое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
            image=cls.img
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='Jane')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_author_client = Client()
        self.post_author_client.force_login(PostPagesTests.author)

        self.not_following_user = User.objects.create_user(username='Jack')
        self.not_following_client = Client()
        self.not_following_client.force_login(self.not_following_user)

        self.follow = Follow.objects.create(
            user=self.user,
            author=PostPagesTests.author
        )

    def test_pages_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_pages_names = {
            reverse('index'): 'index.html',
            reverse('follow_index'): 'follow.html',
            reverse('profile',
                    kwargs={
                        'username': PostPagesTests.author.username
                    }): 'profile.html',
            reverse('group',
                    kwargs={'slug': PostPagesTests.group.slug}): 'group.html',
            reverse('new_post'): 'post_editing.html',
            reverse('post',
                    kwargs={
                        'username': PostPagesTests.author.username,
                        'post_id': PostPagesTests.post.id
                    }): 'post.html',
            reverse('post_edit',
                    kwargs={
                        'username': PostPagesTests.author.username,
                        'post_id': PostPagesTests.post.id
                    }): 'post_editing.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        first_post = response.context.get('page').object_list[0]
        self.assertEqual(first_post.text, PostPagesTests.post.text)
        self.assertEqual(first_post.author, PostPagesTests.author)
        self.assertEqual(first_post.group, PostPagesTests.group)
        self.assertEqual(first_post.image, f'posts/{PostPagesTests.img.name}')

    def test_group_page_shows_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostPagesTests.group.slug})
        )

        first_post = response.context.get('page').object_list[0]
        self.assertEqual(first_post.text, PostPagesTests.post.text)
        self.assertEqual(first_post.author, PostPagesTests.author)
        self.assertEqual(first_post.group, PostPagesTests.group)
        self.assertEqual(first_post.image, f'posts/{PostPagesTests.img.name}')

        group = response.context.get('group')
        self.assertEqual(group, PostPagesTests.group)

    def test_another_group_page_is_empty(self):
        """Пост не отображается в группе, для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('group',
                    kwargs={'slug': PostPagesTests.another_group.slug})
        )
        group_posts = response.context.get('page').object_list
        self.assertFalse(group_posts)

    def test_user_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile',
                    kwargs={'username': PostPagesTests.author.username})
        )

        author = response.context.get('author')
        self.assertEqual(author, PostPagesTests.author)

        john_posts_count = (Post.objects.filter(
                            author=PostPagesTests.author).count())
        posts_count = response.context.get('posts_count')
        self.assertEqual(posts_count, john_posts_count)

        first_post = response.context.get('page').object_list[0]
        self.assertEqual(first_post.text, PostPagesTests.post.text)
        self.assertEqual(first_post.author, PostPagesTests.author)
        self.assertEqual(first_post.group, PostPagesTests.group)
        self.assertEqual(first_post.image, f'posts/{PostPagesTests.img.name}')

    def test_post_page_shows_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={
                        'username': PostPagesTests.author.username,
                        'post_id': PostPagesTests.post.id
                    })
        )
        author = response.context.get('author')
        self.assertEqual(author, PostPagesTests.author)

        john_posts_count = (Post.objects.filter(
                            author=PostPagesTests.author).count())
        posts_count = response.context.get('posts_count')
        self.assertEqual(posts_count, john_posts_count)

        post = response.context.get('post')
        self.assertEqual(post.text, PostPagesTests.post.text)
        self.assertEqual(post.author, PostPagesTests.author)
        self.assertEqual(post.group, PostPagesTests.group)
        self.assertEqual(post.image, f'posts/{PostPagesTests.img.name}')

    def test_new_post_page_shows_correct_context(self):
        """Шаблон post_editing сформирован с правильным контекстом
        для страницы new_post.
        """
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон post_editing сформирован с правильным контекстом
        для страницы post_edit.
        """
        response = self.post_author_client.get(
            reverse('post_edit',
                    kwargs={
                        'username': PostPagesTests.author.username,
                        'post_id': PostPagesTests.post.id
                    })
        )
        form_fields = {
            'text': PostPagesTests.post.text,
            'group': PostPagesTests.group.id,
        }
        for value, content in form_fields.items():
            with self.subTest(value=value):
                form_content = response.context['form'].initial[value]
                self.assertEqual(form_content, content)

    def test_follow_page_shows_correct_context(self):
        """Шаблон follow сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('follow_index'))
        first_post = response.context.get('page').object_list[0]
        self.assertEqual(first_post.text, PostPagesTests.post.text)
        self.assertEqual(first_post.author, PostPagesTests.author)
        self.assertEqual(first_post.group, PostPagesTests.group)
        self.assertEqual(first_post.image, f'posts/{PostPagesTests.img.name}')

    def test_post_is_not_shown_in_not_subscribed_users_feed(self):
        """Пост не отображается в ленте пользователей, не подписанных
        на его автора.
        """
        response = self.not_following_client.get(reverse('follow_index'))
        feed_posts = response.context.get('page').object_list
        self.assertFalse(feed_posts)

    def test_follow_author(self):
        """Авторизованный пользователь может подписываться
        на других пользователей"""
        self.authorized_client.get(reverse(
            'profile_follow',
            kwargs={'username': self.not_following_user.username, }
        ))
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.not_following_user
        ).exists())

    def test_unfollow_author(self):
        """Авторизованный пользователь может удалять авторов из подписок"""
        self.authorized_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': self.follow.author.username, }
        ))
        self.assertFalse(Follow.objects.filter(
            user=self.user, author=self.follow.author
        ).exists())

    def test_index_page_caching(self):
        """Страница index кэшируется с продолжительностью 20 с."""
        response = self.authorized_client.get(reverse('index'))
        initial_page = response.content

        Post.objects.create(
            text='Новый пост',
            author=self.user,
        )
        response = self.authorized_client.get(reverse('index'))
        cached_page = response.content

        time.sleep(20)
        response = self.authorized_client.get(reverse('index'))
        updated_page = response.content
        self.assertEqual(initial_page, cached_page)
        self.assertNotEqual(updated_page, cached_page)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='John')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание'
        )
        cls.per_page = settings.PAGINATOR_PER_PAGE
        for i in range(cls.per_page + 3):
            Post.objects.create(
                text=f'Тестовый текст номер {i}',
                author=cls.author,
                group=cls.group
            )
        cls.user = User.objects.create_user(username='Jane')
        Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTest.user)

        self.pages_with_paginator = [
            reverse('index'),
            reverse('follow_index'),
            reverse('group', kwargs={'slug': PaginatorTest.group.slug}),
            reverse('profile',
                    kwargs={'username': PaginatorTest.author.username}),
        ]

    def test_first_page_contains_correct_number_of_records(self):
        for reverse_name in self.pages_with_paginator:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    PaginatorTest.per_page
                )

    def test_second_page_contains_correct_number_of_records(self):
        for reverse_name in self.pages_with_paginator:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    3
                )

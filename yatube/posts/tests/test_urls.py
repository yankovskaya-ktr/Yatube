from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='John')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-group-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create_user(username='Jane')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post_author_client = Client()
        self.post_author_client.force_login(PostsURLTests.author)

        self.unauthorized_urls = [
            '/',
            f'/group/{PostsURLTests.group.slug}/',
            f'/{PostsURLTests.author.username}/',
            f'/{PostsURLTests.author.username}/{PostsURLTests.post.id}/',
        ]
        self.authorized_only_urls = [
            '/new/',
            '/follow/',
            f'/{PostsURLTests.author.username}/follow/',
            f'/{PostsURLTests.author.username}/unfollow/',
            f'/{PostsURLTests.author.username}/'
            f'{PostsURLTests.post.id}/comment/',
        ]
        self.post_author_only_urls = [
            f'/{PostsURLTests.author.username}/{PostsURLTests.post.id}/edit/',
        ]

    def test_urls_available_for_all_users(self):
        """Страницы доступны любому пользователю."""
        for url in self.unauthorized_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_available_for_authorized_users(self):
        """Страницы доступны авторизованному пользователю."""
        for url in self.authorized_only_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_available_for_post_author(self):
        """Страницы доступны авторизованному пользователю - автору поста."""
        for url in self.post_author_only_urls:
            with self.subTest(url=url):
                response = self.post_author_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_available_for_authorized_redirect_anonymous(self):
        """Страницы, доступные только авторизованным пользователям,
        перенаправляют анонимного пользователя на страницу логина.
        """
        for url in self.authorized_only_urls + self.post_author_only_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_urls_available_for_post_author_redirects_not_author(self):
        """Страницы, доступные только автору поста, перенаправляют авторизованного
        пользователя - не автора.
        """
        for url in self.post_author_only_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertRedirects(response, '/John/1/')

    def test_urls_use_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            '/': 'index.html',
            '/follow/': 'follow.html',
            f'/{PostsURLTests.author.username}/': 'profile.html',
            f'/group/{PostsURLTests.group.slug}/': 'group.html',
            '/new/': 'post_editing.html',
            (f'/{PostsURLTests.author.username}/'
             f'{PostsURLTests.post.id}/'): 'post.html',
            (f'/{PostsURLTests.author.username}/'
             f'{PostsURLTests.post.id}/edit/'): 'post_editing.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.post_author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_available_for_authorized_users(self):
        """Сервер возвращает код 404, если страница не найдена"""
        response = self.guest_client.get('/not_existing_url/')
        self.assertEqual(response.status_code, 404)

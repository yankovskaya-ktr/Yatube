import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post, User


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.MEDIA_ROOT))
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm
        cls.author = User.objects.create_user(username='John')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Текст имеющегося поста',
            author=cls.author,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.post_author_client = Client()
        self.post_author_client.force_login(PostFormTests.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test_img.gif',
            content=test_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Текст нового поста',
            'group': PostFormTests.group.id,
            'image': uploaded,
        }
        response = self.post_author_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=PostFormTests.group,
                image='posts/test_img.gif',
            ).exists()
        )

    def test_edit_post(self):
        """При редактировании поста изменяется запись в Post"""
        form_data = {
            'text': 'Отредактированный текст'
        }
        self.post_author_client.post(
            reverse(
                'post_edit', kwargs={
                    'username': PostFormTests.author.username,
                    'post_id': PostFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.get(id=PostFormTests.post.id).text,
            form_data['text']
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CommentForm
        cls.author = User.objects.create_user(username='John')
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.author,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Jane')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        """Валидная форма создает запись в Comment."""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Текст комментария',
        }
        response = self.authorized_client.post(
            reverse('add_comment', kwargs={
                    'username': CommentFormTests.author.username,
                    'post_id': CommentFormTests.post.id}
                    ),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('post', kwargs={
            'username': CommentFormTests.author.username,
            'post_id': CommentFormTests.post.id}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
            ).exists()
        )

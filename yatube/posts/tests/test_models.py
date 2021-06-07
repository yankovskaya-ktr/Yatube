from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user('John')
        cls.post = Post.objects.create(
            author=author,
            text='f' * 50,
        )

    def test_str_method(self):
        """__str__ содержит первые 15 символов текста"""
        post = PostModelTest.post
        str_field = post.__str__()
        self.assertEqual(str_field, post.text[:15])


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Это группа для тестирования',
        )

    def test_str_method(self):
        """__str__ содержит title группы"""
        group = GroupModelTest.group
        str_field = group.__str__()
        self.assertEqual(str_field, group.title)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user('John')
        user = User.objects.create_user('Jane')
        cls.post = Post.objects.create(
            author=author,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=user,
            text='Тестовый комментарий',
        )

    def test_str_method(self):
        """__str__ содержит первые 15 символов комментария"""
        comment = CommentModelTest.comment
        str_field = comment.__str__()
        self.assertEqual(str_field, comment.text[:15])


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('John')
        cls.user = User.objects.create_user('Jane')
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user,
        )

    def test_str_method(self):
        """__str__ содержит корректную информацию"""
        follow = FollowModelTest.follow
        str_field = follow.__str__()
        self.assertEqual(str_field,
                         f'{FollowModelTest.user.username} подписан на '
                         f'{FollowModelTest.author.username}')

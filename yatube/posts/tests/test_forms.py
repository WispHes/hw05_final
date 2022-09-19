import shutil
import tempfile
from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings

from posts.models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='user_author')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='first'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group
        )
        cls.PROFILE = reverse(
            'posts:profile',
            kwargs={'username': cls.post.author}
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_CREATE = reverse('posts:post_create')
        cls.EDIT = reverse(
            'posts:edit',
            kwargs={'post_id': cls.post.id}
        )
        cls.COMMENT_POST = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id}
        )
        cls.NEW_OBJECTS: int = 1
        cls.post_count = Post.objects.count()
        cls.comment_count = Comment.objects.count()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        self.guest_client = Client()

    def check_form(self, form_data, name_form, image_way):
        """Вспомогательная функция для проверки соответствия переданных форм"""
        self.assertEqual(name_form.group.id, form_data['group'])
        self.assertEqual(name_form.text, form_data['text'])
        self.assertEqual(name_form.author, self.user_author)
        self.assertEqual(name_form.image, image_way)

    def test_create_post(self):
        """Проверка формы создания поста"""
        Post.objects.all().delete()
        form_data = {
            'text': 'Указываем текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            self.POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.PROFILE)
        self.assertEqual(
            Post.objects.count(), self.NEW_OBJECTS
        )
        self.check_form(form_data, Post.objects.last(), 'posts/small.gif')

    def test_edit_post(self):
        """Проверка формы редактирования поста"""
        uploaded = SimpleUploadedFile(
            name='all.gif',
            content=self.small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Взяли и отредактировали текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.EDIT,
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(Post.objects.count(), self.post_count)
        self.check_form(form_data, edited_post, 'posts/all.gif')

    def test_comment_post_author(self):
        """Проверка комментариев для авторизованного пользователя"""
        Comment.objects.all().delete()
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            self.COMMENT_POST,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Comment.objects.count(), self.NEW_OBJECTS
        )
        comment = Comment.objects.last()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user_author)
        self.assertEqual(comment.post.id, self.post.id)

    def test_comment_post_guest(self):
        """Проверка комментариев для неавторизованного пользователя"""
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.guest_client.post(
            self.COMMENT_POST,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Comment.objects.count(), self.comment_count
        )

import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache

from posts.models import Group, Post, User
from posts.forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
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
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.second_group = Group.objects.create(
            title='Это вторая тестовая группа',
            description='Это тестовое описание',
            slug='second-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.URLS = [
            (reverse('posts:index'), True),
            (reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ), True),
            (reverse(
                'posts:profile',
                kwargs={'username': cls.post.author}
            ), True),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ), False),
        ]
        cls.POST_CREATE = reverse('posts:post_create')
        cls.EDIT = reverse(
            'posts:edit',
            kwargs={'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        cache.clear()

    def test_cache(self):
        """Тестирование кеша"""
        get_posts = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.all().delete()
        get_cache_posts = self.authorized_client.get(
            reverse('posts:index')
        ).content
        self.assertEqual(get_posts, get_cache_posts)
        cache.clear()
        get_posts_after_clear_cache = self.authorized_client.get(
            reverse('posts:index')
        ).content
        self.assertNotEqual(get_cache_posts, get_posts_after_clear_cache)

    def check_create_edit_post(self, response):
        """Проверяем, что в форму передан правильный контекст"""
        field_form = response.context['form']
        self.assertIsInstance(
            field_form,
            PostForm
        )

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.POST_CREATE)
        self.check_create_edit_post(response)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.EDIT)
        self.assertEqual(self.post, response.context['form'].instance)
        self.check_create_edit_post(response)

    def check_post_info(self, post):
        """Проверяем поля обьекта"""
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.image, self.post.image)

    def test_page(self):
        """На страницы передаётся ожидаемое количество объектов"""
        for url, flag in self.URLS:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if flag:
                    self.check_post_info(response.context['page_obj'][0])
                else:
                    self.check_post_info(response.context['detail'])

    def test_group(self):
        """Проверяем, что используемый пост
        не попал в группу, для которой не был предназначен."""
        post_url = (
            reverse(
                'posts:group_list',
                kwargs={'slug': self.second_group.slug}
            ))
        response = self.authorized_client.get(post_url)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_coincidence_group_and_profile(self):
        """Проверяем, что на страницы группы и профиля автора
        мы передаем в контекст объекты группы и автора"""
        urls = [
            (reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ), True),
            (reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            ), False)
        ]
        for url, flag in urls:
            response = self.authorized_client.get(url)
            if flag:
                self.assertEqual(response.context['group'], self.post.group)
            else:
                self.assertEqual(response.context['profile'], self.post.author)

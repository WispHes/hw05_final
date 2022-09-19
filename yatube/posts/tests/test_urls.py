from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='user_author')
        cls.about_author = User.objects.create_user(username='about_author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
            group=cls.group
        )
        cls.all_templates = [
            (reverse(
                'posts:index'), '/', 'posts/index.html'),
            (reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}),
                f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (reverse(
                'posts:profile',
                kwargs={'username': cls.post.author}),
                f'/profile/{cls.post.author}/', 'posts/profile.html'),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}),
                f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
            (reverse(
                'posts:post_create'), '/create/', 'posts/create_post.html'),
            (reverse(
                'posts:edit',
                kwargs={'post_id': cls.post.id}),
                f'/posts/{cls.post.id}/edit/', 'posts/create_post.html'),
        ]
        cls.all_url = [
            (reverse(
                'posts:index'), HTTPStatus.OK),
            (reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}), HTTPStatus.OK),
            (reverse(
                'posts:profile',
                kwargs={'username': cls.post.author}), HTTPStatus.OK),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}), HTTPStatus.OK),
            (reverse(
                'posts:post_create'), HTTPStatus.OK),
            (reverse(
                'posts:edit',
                kwargs={'post_id': cls.post.id}), HTTPStatus.OK),
        ]
        cls.redirects_urls = [
            (reverse(
                'posts:post_create'), '/auth/login/?next=/create/'),
            (reverse(
                'posts:edit',
                kwargs={'post_id': cls.post.id}),
                f'/auth/login/?next=/posts/{cls.post.id}/edit/'),
        ]
        cls.unexisting_page = [
            ('/unexisting_page/', 'core/404.html', HTTPStatus.NOT_FOUND)
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        cache.clear()

    def test_unexisting_page(self):
        """Проверка страницы 404"""
        for url, template, response_status in self.unexisting_page:
            response = self.authorized_client.get(url)
            self.assertTemplateUsed(response, template)
            self.assertEqual(response.status_code, response_status)

    def test_temaples(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, name, template in self.all_templates:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_reverse(self):
        """Проверка соответствия фактических адресов страниц с их именами"""
        for url, name, template in self.all_templates:
            with self.subTest(url=url):
                self.assertEqual(url, name)

    def test_response_status_authorized_client(self):
        """Проверка перенаправлений автора"""
        for url, response_status in self.all_url:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, response_status)

    def test_redirects_guest_client(self):
        """Проверка перенаправлений пользователей"""
        for url, page_address in self.redirects_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, page_address)

    def test_redirects_about_client(self):
        """Проверка перенаправлений не автора"""
        self.authorized_client.force_login(self.about_author)
        response = self.authorized_client.get(reverse(
            'posts:edit',
            kwargs={'post_id': self.post.id}), follow=True)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id})
        )

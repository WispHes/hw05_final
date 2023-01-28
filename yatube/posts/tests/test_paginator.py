from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='user_author')
        cls.ALL_POSTS: int = 13
        cls.DIFFERENCE: int = 1
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.bulk_create(
            Post(
                text=f'Тестовый текст №{one_post}',
                author=cls.user_author,
                group=cls.group
            )for one_post in range(cls.ALL_POSTS)
        )
        cls.PAGE_NUMBER = (
            (cls.ALL_POSTS + settings.COUNT_POST - cls.DIFFERENCE)
            // settings.COUNT_POST
        )
        cls.SECOND_POSTS = (cls.ALL_POSTS
                            - (cls.PAGE_NUMBER - cls.DIFFERENCE)
                            * settings.COUNT_POST)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_page_contains_ten_records(self):
        """Проверяем пагинацию"""
        url_pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author}),
        ]

        for url_page in url_pages:
            with self.subTest(url_page=url_page):
                response = self.authorized_client.get(url_page)
                self.assertEqual(len(
                    response.context['page_obj']
                ), settings.COUNT_POST)
                response = self.authorized_client.get(
                    url_page + f'?page={self.PAGE_NUMBER}'
                )
                self.assertEqual(len(
                    response.context['page_obj']
                ), self.SECOND_POSTS)

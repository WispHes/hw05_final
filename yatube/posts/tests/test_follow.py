from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Post, User


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username='user_author'
        )
        cls.user_follower = User.objects.create(
            username='user_follower'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
        )
        cls.NEW_FOLLOW: int = 1
        cls.UNFOLLOW: int = 0
        cls.FOLLOW_URL = reverse(
            'posts:profile_follow',
            kwargs={'username': cls.user_author}
        )
        cls.UNFOLLOW_URL = reverse(
            'posts:profile_unfollow',
            kwargs={'username': cls.user_author}
        )
        cls.FOLLOW_INDEX_URL = reverse('posts:follow_index')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user_follower)
        Follow.objects.all().delete()
        Follow.objects.create(
            author=self.user_author,
            user=self.user_follower,
        )

    def test_profile_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей"""
        self.client.post(self.FOLLOW_URL)
        follow = Follow.objects.last()
        self.assertEqual(Follow.objects.count(), self.NEW_FOLLOW)
        self.assertEqual(follow.author.id, self.user_author.id)
        self.assertEqual(follow.user.id, self.user_follower.id)

    def test_profile_unfollow(self):
        """Авторизованный пользователь может отписываться
        от других пользователей"""
        self.client.post(self.UNFOLLOW_URL)
        self.assertEqual(Follow.objects.count(), self.UNFOLLOW)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_author,
                author=self.user_follower
            ).exists()
        )

    def test_content_follow(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан"""
        response = self.client.get(self.FOLLOW_INDEX_URL)
        self.assertIn(self.post, response.context['page_obj'])

    def test_content_unfollow(self):
        """Новая запись пользователя не появляется в ленте тех,
        кто не подписан"""
        self.client.force_login(self.user_author)
        response = self.client.get(self.FOLLOW_INDEX_URL)
        self.assertNotIn(self.post, response.context['page_obj'])

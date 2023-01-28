from django.test import TestCase
from posts.models import Group, Post, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        check_value = [
            (self.group, self.group.title),
            (self.post, self.post.text[:Post.LEN_OF_POST])
        ]
        for default_value, expected_value in check_value:
            with self.subTest(default_value=default_value):
                self.assertEqual(
                    expected_value,
                    str(default_value),
                    'ошибка в методе __str__'
                )

    def check_text(self, model_fields, flag):
        for field, expected_value in model_fields:
            with self.subTest(field=field):
                if flag:
                    self.assertEqual(
                        self.post._meta.get_field(field).verbose_name,
                        expected_value
                    )
                else:
                    self.assertEqual(
                        self.post._meta.get_field(field).help_text,
                        expected_value
                    )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = [
            ('text', 'Текст поста'),
            ('pub_date', 'Дата создания'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        ]
        self.check_text(field_verboses, True)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = [
            ('text', 'Текст нового поста'),
            ('author', 'Укажите автора'),
            ('group', 'Группа, к которой будет относиться пост'),
        ]
        self.check_text(field_help_texts, False)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages(self):
        """Тестирование общедоступных страниц"""
        url_names = [
            [self.guest_client, '/', HTTPStatus.OK],
            [self.guest_client, '/group/test-slug/', HTTPStatus.OK],
            [self.guest_client, '/profile/auth/', HTTPStatus.OK],
            [self.guest_client, f'/posts/{self.post.pk}/', HTTPStatus.OK],
            [self.guest_client, '/create/', HTTPStatus.FOUND],
            [self.guest_client, f'/posts/{self.post.pk}/edit/',
                HTTPStatus.FOUND],
        ]
        for client, url, code in url_names:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(
                    code,
                    response.status_code
                )

    def test_pages_for_authorized_users(self):
        """Тестирование страниц для авторизованных пользователей"""
        url_names = [
            [self.authorized_client, '/', HTTPStatus.OK],
            [self.authorized_client, '/group/test-slug/', HTTPStatus.OK],
            [self.authorized_client, '/profile/auth/', HTTPStatus.OK],
            [self.authorized_client, f'/posts/{self.post.pk}/', HTTPStatus.OK],
            [self.authorized_client, '/create/', HTTPStatus.OK],
        ]
        for client, url, code in url_names:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(
                    code,
                    response.status_code
                )

    def test_access_page_author_post(self):
        """Доступность страницы автору поста"""
        url = f'/posts/{self.post.pk}/edit/'
        response = self.authorized_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
            'posts/create_post.html': '/create/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_existent_page(self):
        """Запрос к несуществующей странице должен вернуться ошибку 404"""
        url_names = [
            [self.guest_client, '/unexisting_page/', HTTPStatus.NOT_FOUND],
            [self.authorized_client, '/unexisting_page/',
                HTTPStatus.NOT_FOUND],
        ]
        for client, url, code in url_names:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(
                    code,
                    response.status_code
                )

    def test_page404_correct_template(self):
        """Страница 404 отдаёт кастомный шаблон"""
        template_url_name = {
            'core/404.html': '/qwerty/',
        }
        for template, address in template_url_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

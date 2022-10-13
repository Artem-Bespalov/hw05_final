import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post, User

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': self.user})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_page_uses_correct_template(self):
        """Страница post_edit использует соответствующий шаблон."""
        template_page_name = {
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
            ),
        }
        for template, reverse_name in template_page_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(response.context['page_obj'][0].author, self.user)
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.group.title)
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        )
        self.assertEqual(
            response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.group.title)
        self.assertEqual(
            response.context['page_obj'][0].group.description,
            self.group.description)
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(
            response.context['page_obj'][0].group.title, self.group.title)
        self.assertEqual(
            response.context['page_obj'][0].text, self.post.text)
        self.assertEqual(
            response.context['page_obj'][0].group.slug, self.group.slug)
        self.assertEqual(
            response.context['page_obj'][0].image, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Страница post_detail использует соответствующий шаблон."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context.get('post').group.title, self.group.title
        )
        self.assertEqual(
            response.context.get('post').group.slug, self.group.slug
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_post_create_page_show_correct_context(self):
        """Страница post_create использует соответствующий шаблон."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Страница post_edit использует соответствующий шаблон."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context.get('is_edit'))

    def test_post_added_correctly_user2(self):
        """Пост не попал в группу, для которой не был предназначен."""
        group2 = Group.objects.create(title='Тестовая группа2',
                                      slug='test-slug2',
                                      description='Тестовое описание2')
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text=self.post.text,
            author=self.user2,
            group=group2)
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count)
        self.assertNotIn(post, profile)


class PostPaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        posts = [
            Post(
                text='Текст',
                author=cls.user,
                group=cls.group,
            )
            for _ in range(13)
        ]
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_first_page_records_index(self):
        """Количество постов на первой странице index равно 10"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_records_index(self):
        """Количество постов на второй странице index равно 3"""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_records_group_list(self):
        """Количество постов на первой странице group_list равно 10"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(
            len(response.context['page_obj']), 10)

    def test_second_page_records_group_list(self):
        """Количество постов на второй странице group_list равно 3"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']), 3)

    def test_first_page_records_profile(self):
        """Количество постов на первой странице profile равно 10"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(
            len(response.context['page_obj']), 10)

    def test_second_page_records_profile(self):
        """Количество постов на второй странице profile равно 3"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']), 3)

    def test_post_correct_add(self):
        """Пост при создании добавлен корректно"""
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group)
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index)
        self.assertIn(post, group)
        self.assertIn(post, profile)


class CommentTest(TestCase):
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

    def test_add_comment_not_authorized_user(self):
        """"Комментировать посты может только авторизованный пользователь"""
        comment_count = 0
        form_data = {'text': 'Тестовый комментарий'}
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_add_comment(self):
        """После успешной отправки комментарий появляется на странице поста"""
        form_data = {'text': 'Тестовый комментарий'}
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(reverse(
            'posts:post_detail', args=[self.post.id]))
        self.assertEqual(len(response.context['comments']), 1)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text='Тестовый комментарий',
            ).exists()
        )


class CacheViewsTest(TestCase):
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

    def test_cache_index(self):
        response_1 = self.authorized_client.get(reverse('posts:index')).content
        self.post.delete()
        response_2 = self.authorized_client.get(reverse('posts:index')).content
        self.assertEqual(response_1, response_2)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index')).content
        self.assertNotEqual(response_2, response_3)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_unfollower = User.objects.create_user(username="unfollower")
        cls.user_follower = User.objects.create_user(username='auth')
        cls.user_following = User.objects.create_user(username='auth2')
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовый пост',
        )

    def setUp(self):
        self.auth_client_unfollower = Client()
        self.auth_client_unfollower.force_login(self.user_unfollower)
        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.user_follower)
        self.auth_client_following = Client()
        self.auth_client_following.force_login(self.user_following)

    def test_follow(self):
        """Пользователи могут подписываться на других пользователей"""
        self.auth_client_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Пользователи могут удалять их из подписок других пользователей"""
        self.auth_client_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.auth_client_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username':
                                              self.user_following.username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_new_post_show_follower(self):
        """Новая запись пользователя появляется в ленте тех,
            кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        Follow.objects.create(
            user=self.user_follower, author=self.user_following
        )
        post = Post.objects.create(
            author=self.user_following, text="Новый текст поста"
        )
        response = self.auth_client_follower.get(reverse("posts:follow_index"))
        self.assertIn(post, response.context['page_obj'])
        response = self.auth_client_unfollower.get(
            reverse("posts:follow_index")
        )
        self.assertNotEqual(post, response.context)

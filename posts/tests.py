from django.contrib.auth.models import User
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class PostListViewTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='testUser', password='password')

    def test_can_list_posts(self):
        test_user = User.objects.get(username='testUser')
        Post.objects.create(owner=test_user, title='Test Title')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_create_post(self):
        self.client.login(username='testUser', password='password')
        response = self.client.post('/posts/', {'title': 'a title'})
        count = Post.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_not_logged_in_cant_create_post(self):
        response = self.client.post('/posts/', {'title': 'a title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostDetailViewTests(APITestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username='user1', password='user1')
        user_2 = User.objects.create_user(username='user2', password='user2')
        Post.objects.create(
            owner=user_1, title="User 1's Post", content='User 1 content'
        )
        Post.objects.create(
            owner=user_2, title="User 2's Post", content='User 2 content'
        )

    def test_can_retrieve_post_using_valid_id(self):
        response = self.client.get('/posts/1/')
        self.assertEqual(response.data['title'], "User 1's Post")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_retrieve_with_invalid_post_id(self):
        response = self.client.get('/posts/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_post(self):
        self.client.login(username='user1', password='user1')
        response = self.client.put('/posts/1/', {'title': 'updated title'})
        post = Post.objects.filter(pk=1).first()
        self.assertEqual(post.title, 'updated title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_update_someone_elses_posts(self):
        self.client.login(username='user1', password='user1')
        response = self.client.put('/posts/2/', {'title': 'updated title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')
print("TAGS_URL", TAGS_URL)


class PublicTagsApiTest(TestCase):
    """Test the publicly available tags API"""

    def setup(self):
        self.client = APIClient

    def test_login_required(self):
        """Test that the login is required for retrieving tags"""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@someemail.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        print("TAGS_SERIALIZER", serializer)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            email='some2@some2.none',
            password='test123'
        )
        Tag.objects.create(user=user2, name='fruity')
        tag = Tag.objects.create(user=self.user, name='comfort food')

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating tag with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

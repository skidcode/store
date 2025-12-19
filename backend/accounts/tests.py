from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class ProfileAndPasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", email="tester@example.com", password="oldpass123"
        )
        self.client.force_authenticate(self.user)

    def test_get_profile(self):
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "tester")

    def test_update_profile(self):
        resp = self.client.patch(
            "/api/auth/me/",
            {"first_name": "John", "city": "City"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.city, "City")

    def test_change_password(self):
        resp = self.client.post(
            "/api/auth/change-password/",
            {"old_password": "oldpass123", "new_password": "newStrongPass456"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newStrongPass456"))

    def test_change_password_wrong_old(self):
        resp = self.client.post(
            "/api/auth/change-password/",
            {"old_password": "wrongpass", "new_password": "anotherPass789"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

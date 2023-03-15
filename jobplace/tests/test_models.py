from django.contrib.auth import get_user_model 
from django.test import TestCase

class TestCustomUser(TestCase):

    def test_post_login(self):
        user = get_user_model().objects.create_user('user',password='pass')
 
        self.assertEqual(user.login_count,0)
        user.post.login()
        self.assertEqual(user.login_count,1)
        self.assertEqual(get_user_model().objects.get(pk=user.id).login_count,1)
 


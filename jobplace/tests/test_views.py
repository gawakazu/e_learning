from django.contrib.auth import get_user_model 
from django.test import TestCase

class TestRegisterView(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='kazuhiro',password='1234kazu')
        self.user2 = get_user_model().objects.create_user(username='kazuhiro01',password='1234kazu01')

    def test_get_succcess(self):
        #response = self.client.get('/account/register/')
        response = self.client.get('/login/')
        self.assertEqual(response.status_code ,200)
        self.assertFalse(response.content['form'].errors)
        #self.assertTemplateUsed(response,'accounts/register.html')
        self.assertTemplateUsed(response,'accounts/register.html')

    def test_get_by_unauthenticated_user(self):
        logged_in = self.client.login(username=self.user.username,password='1234kazu')
        self.assertTrue(logged_in)       
        response=self.client.get('/kanri/')
        self.assertEqual(response.status_code,200)

        logged_in = self.client.login(username=self.user2.username,password='1234kazu01')
        self.assertTrue(logged_in)
        response=self.client.get('/kanri/')
        self.assertEqual(response.status_code,403)
        response=self.client.get('/information/')
        self.assertEqual(response.status_code,200)



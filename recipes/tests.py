from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from .models import Recipes


class GetPagesTestCase(TestCase):
    fixtures = ['recipes_recipes.json', 'recipes_category.json', 'recipes_tagpost.json'] # файлы JSON
    def setUp(self):
        "Инициализация перед выполнением каждого теста"

    def test_mainpage(self):
        path = reverse('home')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # self.assertIn('recipes/index.html', response.template_name)
        self.assertTemplateUsed(response, 'recipes/index.html')
        self.assertEqual(response.context_data['title'], 'Главная страница')

    def test_redirect_addpage(self):
        path = reverse('add_page')
        redirect_uri = reverse('users:login') + '?next=' + path
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)

    def test_data_mainpage(self):
        r = Recipes.published.all().select_related('cat')
        path = reverse('home')
        response = self.client.get(path)
        print(r)

    def tearDown(self):
        "Действия после выполнения каждого теста"

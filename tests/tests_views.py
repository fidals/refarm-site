"""
Defines tests for views in Catalog app
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from pages.models import Page, get_or_create_struct_page


class PageTests(TestCase):

    urls = 'tests.urls'

    @classmethod
    def setUpClass(cls):
        super(PageTests, cls).setUpClass()

        # -- set up section navi --
        cls.section_navi = Page.objects.create(
            title='Navigation on SE web portal',
            slug='navigation'
        )

        cls.page_default_contacts = Page.objects.create(
            slug='contacts',
            parent=cls.section_navi,
            title='Here you can see Fenichs contacts. He reads every mail!',
            menu_title='contacts',
        )

        cls.page_default_delivery = Page.objects.create(
            slug='delivery',
            parent=cls.section_navi,
            title='How SE logistic system works',
            menu_title='delivery'
        )

        # -- set up section news --
        cls.section_news = Page.objects.create(
            title='News of SE corporation',
            slug='news'
        )

        cls.page_default_ipo = Page.objects.create(
            slug='se-ipo',
            parent=cls.section_news,
            title='ShopElectro go to IPO only after 15-n investment rounds'
        )

        cls.page_default_jobs = Page.objects.create(
            slug='fenich-new-jobs',
            parent=cls.section_news,
            title='Why Fenich called as new Steve Jobs'
        )

    def test_empty_pages_list(self):
        """
        Empty pages list should return 200 response and user friendly message
        """
        section_empty = Page.objects.create(
            slug='empty-section',
            title='Empty pages list'
        )
        response = self.client.get(section_empty.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No sub pages')

    def test_pages_list(self):
        """Page section should contain it's children"""
        section = self.section_navi
        child_fist = self.page_default_contacts
        child_second = self.page_default_delivery
        response = self.client.get(section.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, child_fist.title)
        self.assertContains(response, child_fist.get_absolute_url())

        self.assertContains(response, child_second.title)
        self.assertContains(response, child_second.get_absolute_url())

    def test_nested_page_redirects(self):
        """
        Suppose page "contacts" in DB have url /navi/contacts/. Then:
        /contacts/ --301--> /navi/contacts/
        """
        page = self.page_default_contacts
        url = '/contacts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, page.get_absolute_url())

    def test_nested_page_not_found(self):
        """
        Suppose page "contacts" in DB have url /navi/contacts/. Then:
        /news/contacts/ return 404 status code
        """
        url = '/news/contacts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_nested_page_render(self):
        """
        Suppose page "contacts" in DB have url /navi/contacts/. Then:
        /navi/contacts/ return 200 status code
        """
        url = '/navigation/contacts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_custom_page_autocreation(self):
        """
        Site app create index page by the first request to it's url.
        Index page is custom page.
        So, every custom page should be autocreated by the fist request to it.
        """
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, settings.PAGES['index']['title'])

    def test_page_crumbs(self):
        """Default page have valid crumbs list"""
        page = self.page_default_contacts
        page_index = get_or_create_struct_page(slug='index')
        crumbs_to_test = [
            page_index.menu_title, page_index.get_absolute_url(),
            page.parent.menu_title, page.parent.get_absolute_url(),
            page.menu_title,
        ]
        response = self.client.get(page.get_absolute_url())
        for crumb in crumbs_to_test:
            self.assertContains(response, crumb)

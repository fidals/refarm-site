from django.test import TestCase, override_settings

from pages.models import FlatPage, CustomPage


class PageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PageTests, cls).setUpClass()

        cls.index = CustomPage.objects.create(slug='')
        # -- set up section navi --
        cls.section_navi = FlatPage.objects.create(
            h1='Navigation on web portal',
            slug='navigation'
        )

        cls.page_default_contacts = FlatPage.objects.create(
            slug='contacts',
            parent=cls.section_navi,
            h1='Here you can see Fenichs contacts. He reads every mail!',
            menu_title='contacts',
        )

        cls.page_default_delivery = FlatPage.objects.create(
            slug='delivery',
            parent=cls.section_navi,
            h1='How logistic system works',
            menu_title='delivery'
        )

        # -- set up section news --
        cls.section_news = FlatPage.objects.create(
            h1='News of corporation',
            slug='news'
        )

        cls.page_default_ipo = FlatPage.objects.create(
            slug='se-ipo',
            parent=cls.section_news,
            h1='Our site go to IPO only after 15-n investment rounds'
        )

        cls.page_default_jobs = FlatPage.objects.create(
            slug='fenich-new-jobs',
            parent=cls.section_news,
            h1='Why Fenich called as new Steve Jobs'
        )

    def test_empty_pages_list(self):
        """
        Empty pages list should return 200 response and user friendly message
        """
        section_empty = FlatPage.objects.create(
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
        response = self.client.get(section.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, child_fist.title)
        self.assertContains(response, child_fist.url)

        self.assertContains(response, child_second.title)
        self.assertContains(response, child_second.url)

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

    def test_page_crumbs(self):
        """Default page have valid crumbs list"""
        page = self.page_default_contacts
        page_index, _ = CustomPage.objects.get_or_create(slug='')
        crumbs_to_test = [
            page_index.menu_title, page_index.get_absolute_url(),
            page.parent.menu_title, page.parent.get_absolute_url(),
            page.menu_title,
        ]
        response = self.client.get(page.get_absolute_url())
        for crumb in crumbs_to_test:
            self.assertContains(response, crumb)

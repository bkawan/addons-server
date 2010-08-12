import test_utils
from nose.tools import eq_
from pyquery import PyQuery as pq

from amo.urlresolvers import reverse
from bandwagon.models import Collection
from users.models import UserProfile


class AjaxTest(test_utils.TestCase):
    fixtures = ('base/apps', 'base/users', 'base/addon_3615',
                'base/addon_5299_gcal',
                'base/collections')

    def setUp(self):
        assert self.client.login(username='clouserw@gmail.com',
                                 password='yermom')
        self.user = UserProfile.objects.get(email='clouserw@gmail.com')
        self.other = UserProfile.objects.exclude(id=self.user.id)[0]

    def test_list_collections(self):
        r = self.client.get(reverse('collections.ajax_list')
                            + '?addon_id=3615',)
        doc = pq(r.content)
        eq_(doc('li').attr('data-id'), '80')

    def test_add_collection(self):
        r = self.client.post(reverse('collections.ajax_add'),
                             {'addon_id': 3615, 'id': 80}, follow=True,
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        doc = pq(r.content)
        eq_(doc('li.selected').attr('data-id'), '80')

    def test_bad_collection(self):
        r = self.client.post(reverse('collections.ajax_add'), {'id': 'adfa'})
        eq_(r.status_code, 400)

    def test_remove_collection(self):
        r = self.client.post(reverse('collections.ajax_remove'),
                             {'addon_id': 1843, 'id': 80}, follow=True)
        doc = pq(r.content)
        eq_(len(doc('li.selected')), 0)

    def test_new_collection(self):
        num_collections = Collection.objects.all().count()
        r = self.client.post(reverse('collections.ajax_new'),
                {'addon_id': 5299,
                 'name': 'foo',
                 'slug': 'auniqueone',
                 'description': 'yermom',
                 'listed': True},
                follow=True)
        doc = pq(r.content)
        eq_(len(doc('li.selected')), 1, "The new collection is not selected.")
        eq_(Collection.objects.all().count(), num_collections + 1)

    def test_add_other_collection(self):
        "403 when you try to add to a collection that isn't yours."
        c = Collection(author=self.other)
        c.save()

        r = self.client.post(reverse('collections.ajax_add'),
                             {'addon_id': 3615, 'id': c.id}, follow=True)
        eq_(r.status_code, 403)

    def test_remove_other_collection(self):
        "403 when you try to add to a collection that isn't yours."
        c = Collection(author=self.other)
        c.save()

        r = self.client.post(reverse('collections.ajax_remove'),
                             {'addon_id': 3615, 'id': c.id}, follow=True)
        eq_(r.status_code, 403)

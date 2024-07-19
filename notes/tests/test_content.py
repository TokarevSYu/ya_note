from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NoteTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user',
                                            password='password')
        cls.notes = [
            Note.objects.create(
                title=f'Note {index}',
                text='Just a note.',
                author=cls.user,
                slug=f'note-{index}'
            )
            for index in range(5)
        ]
        cls.home_url = reverse('notes:home')


class TestHomePage(NoteTestBase):

    def test_notes_display(self):
        response = self.client.get(self.home_url)
        for note in self.notes:
            self.assertContains(response, note.title)

    def test_notes_order(self):
        response = self.client.get(self.home_url)
        notes = response.context['object_list']
        all_dates = [note.pk for note in notes]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(NoteTestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = cls.notes[0]
        cls.detail_url = reverse('notes:detail', args=[cls.note.slug])

    def test_note_detail(self):
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_note_not_visible_to_other_users(self):
        another_user = User.objects.create_user(username='another_user',
                                                password='password')
        self.client.login(username='another_user', password='password')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 404)


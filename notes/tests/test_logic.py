from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NoteTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='author',
                                            password='password')
        cls.auth_client = cls.client_class()
        cls.auth_client.login(username='author', password='password')

        cls.another_user = User.objects.create_user(username='reader',
                                                    password='password')
        cls.another_auth_client = cls.client_class()
        cls.another_auth_client.login(username='reader', password='password')

        cls.note = Note.objects.create(
            title='Test Note',
            text='Test content',
            author=cls.user,
            slug='test-note'
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=[cls.note.slug])
        cls.delete_url = reverse('notes:delete', args=[cls.note.slug])
        cls.form_data = {'title': 'Updated Note Title',
                         'text': 'Updated Note content'}


class TestNoteCreation(NoteTestBase):

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response,
                             f"{reverse('users:login')}?next={self.add_url}")
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_authorized_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.last()
        self.assertEqual(note.title, 'Updated Note Title')
        self.assertEqual(note.text, 'Updated Note content')
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(NoteTestBase):

    def test_author_can_edit_note(self):
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note Title')
        self.assertEqual(self.note.text, 'Updated Note content')

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_auth_client.post(self.edit_url,
                                                 data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Test Note')

    def test_author_can_delete_note(self):
        response = self.auth_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.another_auth_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

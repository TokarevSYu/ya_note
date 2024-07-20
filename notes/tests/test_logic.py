from .test_base import TestNote
from notes.models import Note


class TestNoteActions(TestNote):

    def test_create_note(self):
        response = self.author_client.post(self.ADD_URL, data={
            'title': 'New Note',
            'text': 'This is a new note.',
            'slug': 'new-note'
        })
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_edit_note(self):
        response = self.author_client.post(self.EDIT_URL, data={
            'title': 'Updated Note',
            'text': 'Updated content.',
            'slug': 'updated-note'
        })
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')
        self.assertEqual(self.note.text, 'Updated content.')

    def test_delete_note(self):
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertFalse(Note.objects.filter(slug=self.note.slug).exists())

    def test_non_author_cannot_edit_note(self):
        response = self.non_author_client.post(self.EDIT_URL, data={
            'title': 'Hacked Note',
            'text': 'Hacked content.',
            'slug': 'hacked-note'
        })
        self.assertEqual(response.status_code, 404)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, 'Hacked Note')

    def test_non_author_cannot_delete_note(self):
        response = self.non_author_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(slug=self.note.slug).exists())

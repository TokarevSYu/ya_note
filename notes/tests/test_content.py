from notes.forms import NoteForm
from .test_base import TestNote


class TestNotesContent(TestNote):

    def test_note_visibility_for_users(self):
        self.assertTrue(
            self.note in self.author_client.get(self.LIST_URL
                                                ).context['object_list']
        )
        self.assertFalse(
            self.note in self.non_author_client.get(self.LIST_URL
                                                    ).context['object_list']
        )

    def test_form_presence_on_pages(self):
        for url in [self.ADD_URL, self.EDIT_URL]:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_detail_visibility(self):
        response = self.author_client.get(self.detail_url)
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

        response = self.non_author_client.get(self.detail_url)
        self.assertEqual(response.status_code, 404)

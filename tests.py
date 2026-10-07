# notes/tests.py
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import NoteForm
from .models import Note


def make_note(title="Test Note", content="This is a test note."):
    """Helper to create a Note with sensible defaults."""
    return Note.objects.create(title=title, content=content)


class NoteModelTest(TestCase):
    def setUp(self):
        self.note = make_note()

    def test_note_has_title(self):
        self.assertEqual(self.note.title, "Test Note")

    def test_note_has_content(self):
        self.assertEqual(self.note.content, "This is a test note.")

    def test_str_returns_title(self):
        self.assertEqual(str(self.note), "Test Note")

    def test_created_at_is_set_automatically(self):
        self.assertIsNotNone(self.note.created_at)

    def test_created_at_does_not_change_on_save(self):
        original = self.note.created_at
        self.note.title = "Changed"
        self.note.save()
        self.note.refresh_from_db()
        self.assertEqual(self.note.created_at, original)

    def test_updated_at_changes_on_save(self):
        past = timezone.now() - timedelta(days=1)
        Note.objects.filter(pk=self.note.pk).update(updated_at=past)
        self.note.refresh_from_db()
        self.note.title = "Changed"
        self.note.save()
        self.note.refresh_from_db()
        self.assertGreater(self.note.updated_at, past)

    def test_notes_are_ordered_newest_first(self):
        now = timezone.now()
        old = make_note(title="Old")
        new = make_note(title="New")
        Note.objects.filter(pk=old.pk).update(
            created_at=now - timedelta(days=2)
        )
        Note.objects.filter(pk=new.pk).update(
            created_at=now - timedelta(days=1)
        )
        titles = [
            n.title for n in Note.objects.filter(pk__in=[old.pk, new.pk])
        ]
        self.assertEqual(titles, ["New", "Old"])

    def test_title_longer_than_255_characters_is_invalid(self):
        note = Note(title="x" * 256, content="Content")
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_blank_title_is_invalid(self):
        note = Note(title="", content="Content")
        with self.assertRaises(ValidationError):
            note.full_clean()

    def test_blank_content_is_invalid(self):
        note = Note(title="Title", content="")
        with self.assertRaises(ValidationError):
            note.full_clean()


class NoteFormTest(TestCase):
    def test_form_is_valid_with_title_and_content(self):
        form = NoteForm(data={"title": "A title", "content": "Some content"})
        self.assertTrue(form.is_valid())

    def test_form_is_invalid_without_title(self):
        form = NoteForm(data={"title": "", "content": "Some content"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_is_invalid_without_content(self):
        form = NoteForm(data={"title": "A title", "content": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_form_rejects_title_over_255_characters(self):
        form = NoteForm(data={"title": "x" * 256, "content": "Content"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_only_contains_title_and_content(self):
        self.assertEqual(list(NoteForm().fields), ["title", "content"])


class NoteUrlTest(TestCase):
    def test_url_paths(self):
        self.assertEqual(reverse("note_list"), "/")
        self.assertEqual(reverse("note_create"), "/note/new/")
        self.assertEqual(reverse("note_detail", args=[1]), "/note/1/")
        self.assertEqual(reverse("note_update", args=[1]), "/note/1/edit/")
        self.assertEqual(reverse("note_delete", args=[1]), "/note/1/delete/")


class NoteListViewTest(TestCase):
    def test_list_view_returns_200(self):
        response = self.client.get(reverse("note_list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_uses_correct_templates(self):
        response = self.client.get(reverse("note_list"))
        self.assertTemplateUsed(response, "notes/note_list.html")
        self.assertTemplateUsed(response, "base.html")

    def test_list_view_shows_page_title(self):
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, "My Notes")

    def test_list_view_displays_notes(self):
        make_note(title="Shopping", content="Milk and eggs")
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, "Shopping")
        self.assertContains(response, "Milk and eggs")

    def test_list_view_shows_message_when_empty(self):
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, "No notes yet")
        self.assertEqual(len(response.context["notes"]), 0)

    def test_list_view_has_links_for_each_note(self):
        note = make_note()
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, reverse("note_detail", args=[note.pk]))
        self.assertContains(response, reverse("note_update", args=[note.pk]))
        self.assertContains(response, reverse("note_delete", args=[note.pk]))

    def test_list_view_shows_newest_note_first(self):
        now = timezone.now()
        old = make_note(title="Old")
        new = make_note(title="New")
        Note.objects.filter(pk=old.pk).update(
            created_at=now - timedelta(days=2)
        )
        Note.objects.filter(pk=new.pk).update(
            created_at=now - timedelta(days=1)
        )
        response = self.client.get(reverse("note_list"))
        titles = [n.title for n in response.context["notes"]]
        self.assertEqual(titles, ["New", "Old"])

    def test_list_view_truncates_long_content_to_25_words(self):
        words = " ".join(f"word{i:02d}" for i in range(1, 31))
        make_note(content=words)
        response = self.client.get(reverse("note_list"))
        self.assertContains(response, "word25")
        self.assertNotContains(response, "word26")


class NoteDetailViewTest(TestCase):
    def setUp(self):
        self.note = make_note(title="Detail Note", content="Detail content")

    def test_detail_view_returns_200(self):
        response = self.client.get(reverse("note_detail", args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_uses_correct_template(self):
        response = self.client.get(reverse("note_detail", args=[self.note.pk]))
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_detail_view_shows_title_and_content(self):
        response = self.client.get(reverse("note_detail", args=[self.note.pk]))
        self.assertContains(response, "Detail Note")
        self.assertContains(response, "Detail content")

    def test_detail_view_shows_full_content_without_truncating(self):
        words = " ".join(f"word{i:02d}" for i in range(1, 31))
        note = make_note(content=words)
        response = self.client.get(reverse("note_detail", args=[note.pk]))
        self.assertContains(response, "word30")

    def test_detail_view_preserves_line_breaks(self):
        note = make_note(content="line one\nline two")
        response = self.client.get(reverse("note_detail", args=[note.pk]))
        self.assertContains(response, "line one<br>line two")

    def test_detail_view_escapes_html_in_content(self):
        note = make_note(content="<script>alert('hi')</script>")
        response = self.client.get(reverse("note_detail", args=[note.pk]))
        self.assertNotContains(response, "<script>alert")
        self.assertContains(response, "&lt;script&gt;")

    def test_detail_view_returns_404_for_missing_note(self):
        response = self.client.get(reverse("note_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)


class NoteCreateViewTest(TestCase):
    def test_create_view_get_shows_empty_form(self):
        response = self.client.get(reverse("note_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        self.assertIsInstance(response.context["form"], NoteForm)
        self.assertContains(response, "New Note")

    def test_create_view_post_creates_note_and_redirects(self):
        response = self.client.post(
            reverse("note_create"),
            {"title": "New Note", "content": "New content"},
        )
        self.assertRedirects(response, reverse("note_list"))
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, "New Note")
        self.assertEqual(note.content, "New content")

    def test_created_note_appears_on_list_page(self):
        response = self.client.post(
            reverse("note_create"),
            {"title": "Visible Note", "content": "Visible content"},
            follow=True,
        )
        self.assertContains(response, "Visible Note")

    def test_create_view_invalid_data_does_not_create_note(self):
        response = self.client.post(
            reverse("note_create"), {"title": "", "content": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)


class NoteUpdateViewTest(TestCase):
    def setUp(self):
        self.note = make_note(title="Old Title", content="Old content")

    def test_update_view_get_prefills_form(self):
        response = self.client.get(reverse("note_update", args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        self.assertEqual(response.context["form"].instance, self.note)
        self.assertContains(response, "Old Title")
        self.assertContains(response, "Edit Note")

    def test_update_view_post_updates_note_and_redirects(self):
        response = self.client.post(
            reverse("note_update", args=[self.note.pk]),
            {"title": "New Title", "content": "New content"},
        )
        self.assertRedirects(response, reverse("note_list"))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "New Title")
        self.assertEqual(self.note.content, "New content")

    def test_update_view_does_not_create_a_second_note(self):
        self.client.post(
            reverse("note_update", args=[self.note.pk]),
            {"title": "New Title", "content": "New content"},
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_update_view_invalid_data_does_not_change_note(self):
        response = self.client.post(
            reverse("note_update", args=[self.note.pk]),
            {"title": "", "content": "New content"},
        )
        self.assertEqual(response.status_code, 200)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Old Title")
        self.assertEqual(self.note.content, "Old content")

    def test_update_view_returns_404_for_missing_note(self):
        response = self.client.get(reverse("note_update", args=[9999]))
        self.assertEqual(response.status_code, 404)


class NoteDeleteViewTest(TestCase):
    def setUp(self):
        self.note = make_note(title="Delete Me", content="Going away")

    def test_delete_view_get_shows_confirmation_page(self):
        response = self.client.get(reverse("note_delete", args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_confirm_delete.html")
        self.assertContains(response, "Delete Me")

    def test_delete_view_get_does_not_delete_note(self):
        self.client.get(reverse("note_delete", args=[self.note.pk]))
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_delete_view_post_deletes_note_and_redirects(self):
        response = self.client.post(
            reverse("note_delete", args=[self.note.pk])
        )
        self.assertRedirects(response, reverse("note_list"))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_delete_only_removes_the_chosen_note(self):
        other = make_note(title="Keep Me")
        self.client.post(reverse("note_delete", args=[self.note.pk]))
        self.assertTrue(Note.objects.filter(pk=other.pk).exists())

    def test_delete_view_returns_404_for_missing_note(self):
        response = self.client.get(reverse("note_delete", args=[9999]))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse("note_delete", args=[9999]))
        self.assertEqual(response.status_code, 404)

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .forms import NoteForm
from .models import Note


def note_list(request):
    """Read: display all notes."""
    context = {"notes": Note.objects.all(), "page_title": "My Notes"}
    return render(request, "notes/note_list.html", context)


def note_detail(request, pk):
    """Read: display a single note."""
    note = get_object_or_404(Note, pk=pk)
    return render(request, "notes/note_detail.html", {"note": note})


def note_create(request):
    """Create: show form (GET) or save new note (POST)."""
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("note_list")
    else:
        form = NoteForm()
    return render(request, "notes/note_form.html", {"form": form})


def note_update(request, pk):
    """Update: edit an existing note."""
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect("note_list")
    else:
        form = NoteForm(instance=note)
    return render(request, "notes/note_form.html", {"form": form})


def note_delete(request, pk):
    """Delete: confirm (GET), then delete (POST)."""
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        note.delete()
        return redirect("note_list")
    return render(request, "notes/note_confirm_delete.html", {"note": note})

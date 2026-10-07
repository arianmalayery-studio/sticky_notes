# Sticky Notes

A simple sticky notes web app built with Django. Create, view, edit and
delete notes from your browser. The project includes a unit test suite
covering the models, form, URLs and views.

## Features

- View all notes on a single page, newest first (long notes are shortened
  to a preview)
- Open a note to read its full content
- Add a new note
- Edit an existing note
- Delete a note, with a confirmation step before anything is removed
- Form validation (title and content are required, title is limited to
  255 characters)

## Tech stack

- Python 3.12 or newer
- Django 6.1
- SQLite (the default Django database)

## Setup

1. Clone the repository and move into the project folder:

   ```bash
   git clone <your-repository-url>
   cd sticky_notes
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv

   # Windows (PowerShell)
   venv\Scripts\Activate.ps1

   # macOS / Linux
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the database tables:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

   Then open http://127.0.0.1:8000/ in your browser.

## Running the tests

```bash
python manage.py test notes
```

The tests cover:

- **Model:** fields, `__str__`, automatic timestamps, ordering and
  validation
- **Form:** valid and invalid input
- **URLs:** each named route resolves to the expected path
- **Views:** list, detail, create, update and delete, including 404
  responses for missing notes, invalid form data, truncation of long
  content, escaping of HTML, and that deleting requires a POST request

## Project structure

```
sticky_notes/
├── manage.py
├── requirements.txt
├── sticky_notes/        # project settings and root URL configuration
└── notes/               # the notes app
    ├── models.py        # Note model
    ├── forms.py         # NoteForm
    ├── views.py         # list, detail, create, update, delete views
    ├── urls.py          # app URL routes
    ├── tests.py         # unit tests
    ├── templates/       # base.html and the notes templates
    └── static/notes/    # stylesheet
```

## URLs

| Path                    | Name          | Purpose                          |
| ----------------------- | ------------- | -------------------------------- |
| `/`                     | `note_list`   | List all notes                   |
| `/note/new/`            | `note_create` | Add a new note                   |
| `/note/<id>/`           | `note_detail` | View a single note               |
| `/note/<id>/edit/`      | `note_update` | Edit a note                      |
| `/note/<id>/delete/`    | `note_delete` | Confirm and delete a note        |

## Code style

The code is formatted with [Black](https://black.readthedocs.io/) and
checked with [Flake8](https://flake8.pycqa.org/), both configured for a
79-character line length.

```bash
black .
flake8
```

from .dialog import Dialog
from .utils import ADDON_NAME
from aqt import gui_hooks, mw
from aqt.browser import Browser
from aqt.qt import QAction, QMenu


def on_ctx_menu_button(browser: Browser) -> None:
    # This guarantees note IDs are in order selected in browser, as oppose to weird order in browser.selected_notes()
    view = browser.form.tableView
    selection = view.selectionModel().selectedRows()
    # Convert QModelIndex → row numbers (unsorted)
    rows = sorted(idx.row() for idx in selection)
    # Convert each row → note ID
    note_ids = []
    seen_note_ids: set[int] = set()
    for row in rows:
        index = browser.table._model.index(row, 0)
        note_id = browser.table._model.get_note_id(index)
        if note_id not in seen_note_ids:
            seen_note_ids.add(note_id)
            note_ids.append(note_id)

    encoding_window = Dialog(mw, note_ids)
    encoding_window.showMaximized()
    encoding_window.show()
    encoding_window.raise_()
    encoding_window.activateWindow()


def on_browser_ctx_menu(browser: Browser, menu: QMenu) -> None:
    # Example action (enabled only if notes are selected)
    action = QAction(ADDON_NAME, browser)
    action.setEnabled(bool(browser.selectedNotes()))
    action.triggered.connect(lambda: on_ctx_menu_button(browser))
    menu.addSeparator()
    menu.addAction(action)


gui_hooks.browser_will_show_context_menu.append(on_browser_ctx_menu)

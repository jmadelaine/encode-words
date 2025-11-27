from aqt import mw
from aqt.qt import QVBoxLayout, QWidget, QGroupBox, QFormLayout, QComboBox
from .utils import ADDON_DIR, ADDON_NAME, FieldKey
from functools import partial
import json, os
from typing import Callable


FIELD_MAP_CONFIG_PATH = os.path.join(ADDON_DIR, "field-map.json")

FIELD_KEYS: list[FieldKey] = list(FieldKey)

FIELD_LABELS: dict[FieldKey, str] = {
    FieldKey.WORD: "Word",
    FieldKey.WORD_MEANING: "Word meaning",
    FieldKey.WORD_AUDIO: "Word audio",
    FieldKey.SENTENCE: "Sentence",
    FieldKey.SENTENCE_TRANSLATION: "Sentence translation",
    FieldKey.SENTENCE_AUDIO: "Sentence audio",
}


def load_field_mappings() -> dict[str, dict[FieldKey, str]]:
    if not os.path.exists(FIELD_MAP_CONFIG_PATH):
        return {}

    try:
        with open(FIELD_MAP_CONFIG_PATH, "r", encoding="utf-8") as f:
            raw: dict[str, dict[str, str]] = json.load(f)

        parsed: dict[str, dict[FieldKey, str]] = {}

        for note_type_id, inner_map in raw.items():
            converted: dict[FieldKey, str] = {}

            for key_str, value in inner_map.items():
                try:
                    field_key = FieldKey(key_str)
                except ValueError:
                    # If the JSON had a key that is no longer valid,
                    # skip it gracefully.
                    continue

                converted[field_key] = value

            parsed[note_type_id] = converted

        return parsed

    except Exception as e:
        print(f"[{ADDON_NAME}] failed to load field mappings: {e}")
        return {}


def save_field_mappings(mappings: dict[str, dict[FieldKey, str]]):
    os.makedirs(os.path.dirname(FIELD_MAP_CONFIG_PATH), exist_ok=True)

    # Convert FieldKey → its .value
    serializable: dict[str, dict[str, str]] = {}
    for note_type_id, inner_map in mappings.items():
        serializable[note_type_id] = {
            field_key.value: value for field_key, value in inner_map.items()
        }

    with open(FIELD_MAP_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)


class FieldMapPanel(QWidget):
    def __init__(
        self,
        parent: QWidget,
        note_ids: list[int],
        on_mappings_changed: Callable[[dict[str, dict[FieldKey, str]]], None],
    ):
        super().__init__(parent)

        self.on_mappings_changed = on_mappings_changed

        # Load mappings from disk
        self.mappings: dict[str, dict[FieldKey, str]] = load_field_mappings()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # get unique note types
        note_type_ids = list(
            {mw.col.get_note(note_id).note_type()["id"] for note_id in note_ids}
        )

        for note_type_id in note_type_ids:
            note_type = mw.col.models.get(note_type_id)
            field_names = [f["name"] for f in note_type["flds"]]

            group_box = QGroupBox(f'Note type: {note_type["name"]}', self)
            form_layout = QFormLayout(group_box)

            initial_field_mappings: dict[FieldKey, str] = (
                self.mappings.get(str(note_type_id), {}) or {}
            )

            for field_key in FIELD_KEYS:
                combo_box = QComboBox(group_box)
                combo_box.addItem("(Nothing)", userData=None)

                # Populate combo box options
                for field_name in field_names:
                    combo_box.addItem(field_name, userData=field_name)

                # Init to previously stored option if exists
                stored_value = initial_field_mappings.get(field_key)
                item_idx = combo_box.findData(stored_value)
                if item_idx >= 0:
                    combo_box.setCurrentIndex(item_idx)

                combo_box.currentIndexChanged.connect(
                    partial(self.on_field_mapping_change, note_type_id, field_key)
                )

                form_layout.addRow(FIELD_LABELS[field_key], combo_box)

            self.layout.addWidget(group_box)

        # Notify parent once after initial load
        if self.on_mappings_changed:
            self.on_mappings_changed(self.mappings)

    def on_field_mapping_change(self, note_type_id: int, field_key: FieldKey):
        value = self.sender().currentData()
        self.mappings.setdefault(str(note_type_id), {})[field_key] = value

        save_field_mappings(self.mappings)

        # Notify parent on each change
        if self.on_mappings_changed:
            self.on_mappings_changed(self.mappings)

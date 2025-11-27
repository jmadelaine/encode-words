from .card import Card
from .field_map_panel import FieldMapPanel
from .utils import ADDON_NAME, FieldKey
from .utils import CardType, FieldKey
from aqt import mw
from aqt.qt import QDialog, QLabel, QPushButton, QScrollArea, QVBoxLayout
from aqt.qt import QProgressBar


CARD_TYPES = [
    CardType.SEMANTIC_ENCODING,
    CardType.ELABORATIVE_ENCODING,
    CardType.FORM_ENCODING,
]


class Dialog(QDialog):
    # add near top of class

    def __init__(self, parent, note_ids):
        super().__init__(parent)

        self.cards = [
            (note_id, card_type) for card_type in CARD_TYPES for note_id in note_ids
        ]
        self.card_index = 0
        self.field_mappings = {}

        self.setWindowTitle(ADDON_NAME)
        self.resize(900, 600)
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel(f"{len(note_ids)} notes selected", self))

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        mapping_widget = FieldMapPanel(
            parent=self,
            note_ids=note_ids,
            on_mappings_changed=self.set_note_type_field_mappings,
        )
        scroll.setWidget(mapping_widget)
        self.layout.addWidget(scroll)

        start_button = QPushButton("Start", self)
        start_button.clicked.connect(self.show_current_card)
        self.layout.addWidget(start_button)

    def set_note_type_field_mappings(self, mappings: dict[str, dict[FieldKey, str]]):
        self.field_mappings = mappings

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            w = child.widget()
            if w:
                w.deleteLater()

    def show_current_card(self):
        self.clear_layout()

        if self.card_index >= len(self.cards):
            self.show_completion_screen()
            return

        note_id, card_type = self.cards[self.card_index]

        self.progress = QProgressBar(self)
        self.progress.setRange(0, len(self.cards))
        self.progress.setValue(self.card_index)
        self.layout.addWidget(self.progress)

        self.layout.addWidget(
            Card(
                parent=self,
                note_id=note_id,
                card_type=card_type,
                mappings=self.field_mappings,
                on_next=self.on_card_next,
                on_previous=self.on_card_previous if self.card_index > 0 else None,
            )
        )

    def on_card_next(self):
        self.card_index += 1
        self.show_current_card()

    def on_card_previous(self):
        self.card_index = max(0, self.card_index - 1)
        self.show_current_card()

    def show_completion_screen(self):
        self.clear_layout()

        label = QLabel("All cards completed.\nGreat job!", self)
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.accept)

        self.layout.addWidget(label)
        self.layout.addWidget(close_btn)

    def closeEvent(self, evt):
        mw._encoding_win = None
        super().closeEvent(evt)

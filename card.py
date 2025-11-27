from .utils import CardType, FieldKey, furigana_to_html
from aqt import mw, sound
from aqt.qt import Qt, QVBoxLayout, QPushButton, QWidget, QSizePolicy, QHBoxLayout
from aqt.webview import AnkiWebView
import re


audio_icon = '<svg style="width:1.5rem;height:1.5rem" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M760-481q0-83-44-151.5T598-735q-15-7-22-21.5t-2-29.5q6-16 21.5-23t31.5 0q97 43 155 131.5T840-481q0 108-58 196.5T627-153q-16 7-31.5 0T574-176q-5-15 2-29.5t22-21.5q74-34 118-102.5T760-481ZM280-360H160q-17 0-28.5-11.5T120-400v-160q0-17 11.5-28.5T160-600h120l132-132q19-19 43.5-8.5T480-703v446q0 27-24.5 37.5T412-228L280-360Zm380-120q0 42-19 79.5T591-339q-10 6-20.5.5T560-356v-250q0-12 10.5-17.5t20.5.5q31 25 50 63t19 80Z"/></svg>'
writing_icon = '<svg style="width:3rem;height:3rem" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M168-121q-21 5-36.5-10.5T121-168l35-170 182 182-170 35Zm235-84L205-403l413-413q23-23 57-23t57 23l84 84q23 23 23 57t-23 57L403-205Z"/></svg>'
imagery_icon = '<svg style="width:3rem;height:3rem" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m88-304 160-213q6-8 14.5-12t17.5-4q9 0 17.5 4t14.5 12l136 181q6 8 14 12t18 4q25 0 36-22.5t-4-42.5l-84-111q-8-11-8-24t8-24l100-133q6-8 14.5-12t17.5-4q9 0 17.5 4t14.5 12l280 373q15 20 4 42t-36 22H120q-25 0-36-22t4-42Z"/></svg>'
recall_icon = '<svg style="width:3rem;height:3rem" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M360-160H200q-33 0-56.5-23.5T120-240v-560q0-33 23.5-56.5T200-880h560q33 0 56.5 23.5T840-800v560q0 33-23.5 56.5T760-160H600l-92 92q-12 12-28 12t-28-12l-92-92Zm116-120q21 0 35.5-14.5T526-330q0-21-14.5-35.5T476-380q-21 0-35.5 14.5T426-330q0 21 14.5 35.5T476-280Zm70-360q0 17-11 36.5T498-561q-17 15-27.5 28.5T453-505q-4 8-6 16t-4 18q-2 15 8 26t26 11q14 0 25-10t15-27q3-14 11.5-26t27.5-31q35-35 49.5-59t14.5-53q0-54-36.5-87T484-760q-45 0-78 19t-53 53q-7 12-.5 25t20.5 18q13 5 26 0t21-16q11-14 27-22.5t37-8.5q26 0 44 14.5t18 37.5Z"/></svg>'
recognition_icon = '<svg style="width:3rem;height:3rem" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M480-320q75 0 127.5-52.5T660-500q0-75-52.5-127.5T480-680q-75 0-127.5 52.5T300-500q0 75 52.5 127.5T480-320Zm0-72q-45 0-76.5-31.5T372-500q0-45 31.5-76.5T480-608q45 0 76.5 31.5T588-500q0 45-31.5 76.5T480-392Zm0 192q-134 0-244.5-72T61-462q-5-9-7.5-18.5T51-500q0-10 2.5-19.5T61-538q64-118 174.5-190T480-800q134 0 244.5 72T899-538q5 9 7.5 18.5T909-500q0 10-2.5 19.5T899-462q-64 118-174.5 190T480-200Z"/></svg>'
semantic_icon = '<svg style="width:3rem;height:3rem" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M400-240q-33 0-56.5-23.5T320-320v-50q-57-39-88.5-100T200-600q0-117 81.5-198.5T480-880q117 0 198.5 81.5T760-600q0 69-31.5 129.5T640-370v50q0 33-23.5 56.5T560-240H400Zm0 160q-17 0-28.5-11.5T360-120q0-17 11.5-28.5T400-160h160q17 0 28.5 11.5T600-120q0 17-11.5 28.5T560-80H400Z"/></svg>'


class BaseCard(QWidget):
    def __init__(self, parent, note, mappings, on_next, on_previous):
        super().__init__(parent)

        self.note = note
        self.mappings = mappings
        self.on_next = on_next
        self.on_previous = on_previous

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.web = AnkiWebView(self)
        self.web.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
        )
        self.web.set_bridge_command(self._on_pycmd, self)
        self.layout.addWidget(self.web, 1)

        # horizontal layout to right-align the button
        button_row = QHBoxLayout()
        self.layout.addLayout(button_row)

        if on_previous is not None:
            previous_button = QPushButton("Back", self)
            previous_button.setFixedWidth(120)
            previous_button.setFixedHeight(
                int(previous_button.sizeHint().height() * 1.5)
            )
            previous_button.clicked.connect(self.on_previous_button)
            button_row.addWidget(previous_button)

        button_row.addStretch(1)  # push buttons to ends

        next_button = QPushButton("Next", self)
        next_button.setFixedWidth(120)
        next_button.setFixedHeight(int(next_button.sizeHint().height() * 1.5))
        next_button.clicked.connect(self.on_next_button)
        button_row.addWidget(next_button)

        # allows hotkey interactions
        self.setFocus()

    def _on_pycmd(self, cmd: str):
        if cmd.startswith("play:"):
            filename = cmd.split(":", 1)[1]
            self.play_sound(filename)
        elif cmd == "next":
            self.on_next_button()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.on_next_button()
        else:
            super().keyPressEvent(event)

    def get_field(self, field_key):
        field_name = self.mappings.get(str(self.note.note_type()["id"]), {}).get(
            field_key
        )
        return self.note[field_name] if field_name else ""

    def play_sound(self, filename: str):
        # Stop anything currently playing
        try:
            sound.av_player.stop_and_clear_queue()
        except:
            pass  # safe fallback

        if not filename:
            return

        # Use Anki's own sound regex to be safe
        sound_regex = mw.col.media.sound_regexps[0]
        match = re.search(sound_regex, filename)
        if not match:
            return

        sound.av_player.play_file(match.group("fname"))

    def render_content(self, htmlBody):
        html = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                html {{
                    font-size: 16px;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    flex: 1;
                }}
                ruby rt {{ font-size: 0.5em; }}
                </style>
            </head>
            <body>
                {htmlBody}
            </body>
            </html>
            """

        self.web.stdHtml(html, context=mw)

    def on_next_button(self):
        self.on_next()

    def on_previous_button(self):
        self.on_previous()


class SemanticMeaningCard(BaseCard):
    def __init__(self, parent, note, mappings, on_next, on_previous):
        super().__init__(parent, note, mappings, on_next, on_previous)

        self.stage = 0
        self.render_content(
            f"""
                <div style="display:flex;flex-direction:column;flex:1;gap:2rem">
                    <div style="display:flex;justify-content:center;padding-bottom:2rem;opacity:0.5">
                        {semantic_icon}
                    </div>
                    <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                        <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.WORD))}
                            <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.WORD_AUDIO)}')">{audio_icon}</button>
                            </div>
                        </div>
                        <div style="font-size:1.25rem;text-align:center">{self.get_field(FieldKey.WORD_MEANING)}</div>
                    </div>
                </div>
            """
        )
        self.play_sound(self.get_field(FieldKey.WORD_AUDIO))

    def on_next_button(self):
        if self.stage == 0:

            self.stage = 1
            self.render_content(
                f"""
                    <div style="display:flex;flex-direction:column;flex:1;gap:2rem">
                        <div style="display:flex;justify-content:center;padding-bottom:2rem;opacity:0.5">
                            {semantic_icon}
                        </div>
                        <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                            <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.WORD))}
                                <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                    <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.WORD_AUDIO)}')">{audio_icon}</button>
                                </div>
                            </div>
                            <div style="font-size:1.25rem;text-align:center">{self.get_field(FieldKey.WORD_MEANING)}</div>
                        </div>
                        <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                            <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.SENTENCE))}
                                <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                    <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.SENTENCE_AUDIO)}')">{audio_icon}</button>
                                </div>
                            </div>
                            <div style="font-size:1rem;text-align:center">{self.get_field(FieldKey.SENTENCE_TRANSLATION)}</div>
                        </div>
                    </div>
            """
            )
            self.play_sound(self.get_field(FieldKey.SENTENCE_AUDIO))

        else:

            super().on_next_button()


class RecognitionImageryCard(BaseCard):
    def __init__(self, parent, note, mappings, on_next, on_previous):
        super().__init__(parent, note, mappings, on_next, on_previous)

        self.stage = 0
        self.render_content(
            f"""
                <div style="display:flex;flex-direction:column;flex:1;gap:2rem">
                    <div style="display:flex;justify-content:center;padding-bottom:2rem;opacity:0.5">
                        {recognition_icon}
                    </div>
                    <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                        <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.WORD))}
                            <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.WORD_AUDIO)}')">{audio_icon}</button>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                        <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.SENTENCE))}
                            <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.SENTENCE_AUDIO)}')">{audio_icon}</button>
                            </div>
                        </div>
                    </div>
                </div>
            """
        )
        self.play_sound(self.get_field(FieldKey.WORD_AUDIO))

    def on_next_button(self):
        if self.stage == 0:

            self.stage = 1
            self.render_content(
                f"""
                    <div style="display:flex;flex-direction:column;flex:1;gap:2rem">
                        <div style="display:flex;justify-content:center;padding-bottom:2rem;opacity:0.5">
                            {imagery_icon}
                        </div>
                        <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                            <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.WORD))}
                                <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                    <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.WORD_AUDIO)}')">{audio_icon}</button>
                                </div>
                            </div>
                            <div style="font-size:1.25rem;text-align:center">{self.get_field(FieldKey.WORD_MEANING)}</div>
                        </div>
                        <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                            <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.SENTENCE))}
                                <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                    <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.SENTENCE_AUDIO)}')">{audio_icon}</button>
                                </div>
                            </div>
                            <div style="font-size:1rem;text-align:center">{self.get_field(FieldKey.SENTENCE_TRANSLATION)}</div>
                        </div>
                    </div>
            """
            )
            self.play_sound(self.get_field(FieldKey.WORD_AUDIO))

        else:

            super().on_next_button()


class RecallTypingCard(BaseCard):
    def __init__(self, parent, note, mappings, on_next, on_previous):
        super().__init__(parent, note, mappings, on_next, on_previous)

        self.stage = 0
        self.render_content(
            f"""
                <div style="display:flex;flex-direction:column;flex:1;gap:2rem">
                    <div style="display:flex;justify-content:center;padding-bottom:2rem;opacity:0.5">
                        {recall_icon}
                    </div>
                    <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                        <div style="font-size:1.25rem;text-align:center">{self.get_field(FieldKey.WORD_MEANING)}</div>
                    </div>
                    <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                        <div style="font-size:1rem;text-align:center">{self.get_field(FieldKey.SENTENCE_TRANSLATION)}</div>
                    </div>
                </div>
            """
        )

    def on_next_button(self):
        if self.stage == 0:

            self.stage = 1
            self.render_content(
                f"""
                    <div style="display:flex;flex-direction:column;flex:1;gap:2rem">
                        <div style="display:flex;justify-content:center;padding-bottom:2rem;opacity:0.5">
                            {writing_icon}
                        </div>
                        <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                            <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.WORD))}
                                <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                    <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.WORD_AUDIO)}')">{audio_icon}</button>
                                </div>
                            </div>
                            <div style="font-size:1.25rem;text-align:center">{self.get_field(FieldKey.WORD_MEANING)}</div>
                        </div>
                        <div style="display:flex;flex-direction:column;flex:1;gap:1rem;align-items:center">
                            <div style="position:relative;font-size:1.5rem;text-align:center">{furigana_to_html(self.get_field(FieldKey.SENTENCE))}
                                <div style="position:absolute;top:0;left:100%;bottom:0;padding-left:1rem;display:flex;flex-direction:column;justify-content:center;aligm-items:center">
                                    <button style="padding:0;margin:0;display:flex;align-items:center;justify-content:center;width:3rem;height:3rem;border-radius:50%;background:none;border:0;opacity:0.25" onclick="pycmd('play:' + '{self.get_field(FieldKey.SENTENCE_AUDIO)}')">{audio_icon}</button>
                                </div>
                            </div>
                            <div style="font-size:1rem;text-align:center">{self.get_field(FieldKey.SENTENCE_TRANSLATION)}</div>
                        </div>
                        <div style="display:flex;justify-content:center;padding-top:1rem">
                            <input id="textbox" type="text" style="width:300px;padding:0.5rem 1rem;font-size:1.25rem;text-align:center" placeholder="Type the word..."></input>
                        </div>
                    </div>
                    <script>
                        {{
                            document.getElementById("textbox")?.focus()
                        }}
                    </script>
            """
            )
            self.play_sound(self.get_field(FieldKey.WORD_AUDIO))
            self.web.setFocus()

        else:

            super().on_next_button()


CARD_TYPE_MAP = {
    CardType.SEMANTIC_ENCODING: SemanticMeaningCard,
    CardType.ELABORATIVE_ENCODING: RecognitionImageryCard,
    CardType.FORM_ENCODING: RecallTypingCard,
}


class Card(QWidget):
    def __init__(self, parent, note_id, card_type, mappings, on_next, on_previous):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.layout.addWidget(
            CARD_TYPE_MAP[card_type](
                parent=self,
                note=mw.col.get_note(note_id),
                mappings=mappings,
                on_next=on_next,
                on_previous=on_previous,
            )
        )

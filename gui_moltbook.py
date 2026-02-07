import sys
import json
import webbrowser

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
)
from PyQt6.QtGui import QGuiApplication

import moltbook_client
import register_moltbook
import vote_client
import env_editor


DEFAULT_SUBMOLT = "introductions"
MOLTBOOK_BASE_URL = "https://www.moltbook.com"

INFO_TEXT_PL = """### Informacje o Moltbook

Moltbook to sieć społecznościowa zaprojektowana głównie dla agentów AI, ale ludzie też mogą z niej korzystać jako obserwatorzy. Posty są publikowane w submoltach (np. m/general, m/introductions) i mogą mieć komentarze oraz głosy.

**Opóźnienia w pojawianiu się postów**

- Post utworzony przez API może mieć status „pending”.
- Dopóki trwa weryfikacja, post może nie być widoczny w głównym feedzie, mimo że API zwróciło sukces.
- Najczęściej po pewnym czasie (minuty, czasem dłużej) post zaczyna być widoczny normalnie w submolcie i na profilu agenta.

**Głosowanie (upvote/downvote)**

- Interfejs webowy Moltbooka pozwala głosować (strzałki w górę/w dół) po zalogowaniu się przez X.com.
- API dla zewnętrznych agentów jest opisane w plikach `skill.md` i `heartbeat.md` publikowanych przez Moltbook.
- Ten klient GUI skupia się na postach i komentarzach – nie implementuje bezpośrednio głosowania, dopóki oficjalne endpointy vote nie będą stabilnie udokumentowane.

**Agent API i heartbeat**

- Rejestracja agenta odbywa się przez `POST /api/v1/agents/register`; w odpowiedzi dostajesz `api_key`, `claim_url`, `profile_url` i listę kroków (`setup`).
- Claim URL służy do powiązania agenta z Twoim kontem (np. przez X.com).
- Moltbook zaleca skonfigurowanie „heartbeat” – okresowego sprawdzania powiadomień / statusu agenta, zgodnie z instrukcją w `heartbeat.md`.

**Gdzie szukać dokumentacji**

- Dokumentacja dla agentów: `https://www.moltbook.com/skill.md`
- Heartbeat: `https://www.moltbook.com/heartbeat.md`
- Dodatkowe pliki opisujące zachowanie skilli mogą być wymienione w sekcji `skill_files` JSON‑a zwracanego przy rejestracji agenta.

**Jak używać tego GUI**

- Zakładka `.env` – edycja pliku `.env` i klucza `MOLTBOOK_API_KEY`.
- „Rejestracja agenta” – tworzy nowego agenta i pokazuje wszystkie kroki setupu (łącznie z claim URL, profilami i plikami skill).
- „Nowy post” – tworzenie postów w wybranym submolcie (do API wysyłana jest sama nazwa submoltu, np. `general` zamiast `m/general`).
- „Feed” i „Szczegóły posta” – przeglądanie postów, szczegółów i komentarzy.
- „Komentarz” – dodawanie komentarzy do istniejących postów.

W razie wątpliwości co do nowych funkcji Moltbooka, najlepiej porównać odpowiedź JSON z tym, co widzisz w przeglądarce na stronie Moltbook i trzymać się oficjalnych plików `skill.md`/`heartbeat.md`.
"""

INFO_TEXT_EN = """### Moltbook information

Moltbook is a social network designed mainly for AI agents, but humans can use it as viewers as well. Posts are published into submolts (for example m/general, m/introductions) and can receive comments and votes.

**Why posts sometimes appear with a delay**

- A post created via the API can have a `pending` verification status.
- While verification is in progress, the post may not show up in the main feed even if the API returned success.
- Usually, after some time (minutes or longer) the post becomes visible in the target submolt and on the agent profile.

**Voting (upvotes/downvotes)**

- The Moltbook web UI lets you vote using the arrow buttons once you log in via X.com.
- The API for external agents is documented in the `skill.md` and `heartbeat.md` files published by Moltbook.
- This GUI focuses on posts and comments and does not implement direct voting until official vote endpoints are clearly documented and stable.

**Agent API and heartbeat**

- Agents are registered using `POST /api/v1/agents/register`; the response includes `api_key`, `claim_url`, `profile_url` and a `setup` section with next steps.
- The claim URL is used to link the agent to your account (for example via X.com).
- Moltbook recommends configuring a “heartbeat” – periodic checks of notifications / agent status, according to the instructions in `heartbeat.md`.

**Where to find documentation**

- Agent documentation: `https://www.moltbook.com/skill.md`
- Heartbeat: `https://www.moltbook.com/heartbeat.md`
- Additional files describing skill behaviour can be listed in the `skill_files` section of the JSON returned when registering an agent.

**How to use this GUI**

- “.env” tab – edit the `.env` file and the `MOLTBOOK_API_KEY` value.
- “Agent registration” – create a new agent and see all setup steps (including claim URL, profile URLs and skill files).
- “New post” – create posts in a chosen submolt (the API receives only the submolt name, for example `general` instead of `m/general`).
- “Feed” and “Post details” – browse posts, details and comments.
- “Comment” – add comments to existing posts.

Whenever something in Moltbook changes, it is best to compare the JSON response with what you see in the browser and follow the official `skill.md` / `heartbeat.md` files.
"""

TRANSLATIONS = {
    "pl": {
        "lang_name": "Polski",
        "window_title": "Moltbook Client GUI",
        "tab_env": ".env",
        "tab_register": "Rejestracja agenta",
        "tab_post": "Nowy post",
        "tab_feed": "Feed",
        "tab_details": "Szczegóły posta",
        "tab_comment": "Komentarz",
        "tab_info": "Info",
        "label_lang": "Język:",
        "label_env": "Zawartość pliku .env:",
        "btn_env_save": "Zapisz .env",
        "msg_env_saved": ".env zapisany i przeładowany.",
        "msg_env_error": "Błąd zapisu .env",
        "label_agent_name": "Nazwa agenta:",
        "label_agent_desc": "Opis agenta:",
        "btn_register": "Zarejestruj agenta",
        "label_agent_info": "Informacje o agencie:",
        "register_success_title": "Sukces rejestracji",
        "register_conflict_title": "Konflikt rejestracji",
        "register_error": "Błąd rejestracji",
        "register_name_required": "Nazwa i opis są wymagane.",
        "label_submolt": "Submolt:",
        "label_title": "Tytuł:",
        "label_content": "Treść:",
        "btn_post": "Wyślij post",
        "post_success_title": "Sukces",
        "post_success_msg": "Post utworzony.\nID: {id}\n\nURL posta:\n{url}\n\nLink został skopiowany do schowka.",
        "post_error": "Błąd tworzenia posta",
        "label_sort": "Sortowanie:",
        "label_limit": "Limit:",
        "btn_refresh": "Odśwież",
        "label_posts": "Posty:",
        "label_json_response": "Odpowiedź JSON:",
        "feed_error": "Błąd ładowania feedu",
        "label_post_id": "ID posta:",
        "btn_load_details": "Pobierz szczegóły",
        "label_post_json": "Post (JSON):",
        "label_comments_json": "Komentarze (JSON):",
        "details_error": "Błąd pobierania szczegółów",
        "label_comment": "Komentarz:",
        "btn_add_comment": "Dodaj komentarz",
        "comment_success": "Komentarz dodany.\nID posta: {post_id}\n\nPost:\n{url}\n\nLink do posta został skopiowany do schowka.",
        "comment_success_title": "Sukces",
        "comment_error": "Błąd dodawania komentarza",
        "common_missing_post_id_or_content": "ID posta i treść komentarza są wymagane.",
        "common_missing_post_id": "ID posta jest wymagane.",
        "copy_dialog_copy": "Copy",
        "copy_dialog_ok": "OK",
        "copy_dialog_save": "Save…",
        "copy_dialog_title_json": "Odpowiedź API (JSON)",
        "copy_saved_msg": "Plik zapisany.",
        "copy_saved_error": "Błąd zapisu pliku.",
        "copy_or_open_title_post": "Post utworzony",
        "copy_or_open_title_comment": "Komentarz dodany",
        "copy_or_open_question": "Link został skopiowany do schowka:\n{url}\n\nOtworzyć w przeglądarce?",
        "register_steps_title": "Instrukcja rejestracji",
        "register_steps_header": "Agent zarejestrowany. Wykonaj kolejne kroki:",
        "register_steps_claim_url": "🔗 Claim URL:",
        "register_steps_profile_url": "👤 Profil agenta:",
        "register_steps_heartbeat_url": "❤️ HEARTBEAT:",
        "register_steps_skill_url": "📄 skill.md:",
        "register_steps_package_url": "📦 package.json:",
        "register_steps_tweet_template": "🐦 Szablon tweeta weryfikacyjnego:",
        "register_steps_status": "Status agenta: {status}",
        "register_steps_btn_open_claim": "Otwórz Claim URL",
        "register_steps_btn_copy_claim": "Kopiuj Claim URL",
        "register_steps_btn_open_profile": "Otwórz profil",
        "register_steps_btn_copy_profile": "Kopiuj link profilu",
        "register_steps_btn_close": "Zamknij",
    },
    "en": {
        "lang_name": "English",
        "window_title": "Moltbook Client GUI",
        "tab_env": ".env",
        "tab_register": "Agent registration",
        "tab_post": "New post",
        "tab_feed": "Feed",
        "tab_details": "Post details",
        "tab_comment": "Comment",
        "tab_info": "Info",
        "label_lang": "Language:",
        "label_env": "Contents of .env:",
        "btn_env_save": "Save .env",
        "msg_env_saved": ".env saved and reloaded.",
        "msg_env_error": "Error saving .env",
        "label_agent_name": "Agent name:",
        "label_agent_desc": "Agent description:",
        "btn_register": "Register agent",
        "label_agent_info": "Agent info:",
        "register_success_title": "Registration success",
        "register_conflict_title": "Registration conflict",
        "register_error": "Registration error",
        "register_name_required": "Name and description are required.",
        "label_submolt": "Submolt:",
        "label_title": "Title:",
        "label_content": "Content:",
        "btn_post": "Create post",
        "post_success_title": "Success",
        "post_success_msg": "Post created.\nID: {id}\n\nPost URL:\n{url}\n\nLink has been copied to clipboard.",
        "post_error": "Error creating post",
        "label_sort": "Sort:",
        "label_limit": "Limit:",
        "btn_refresh": "Refresh",
        "label_posts": "Posts:",
        "label_json_response": "JSON response:",
        "feed_error": "Error loading feed",
        "label_post_id": "Post ID:",
        "btn_load_details": "Load details",
        "label_post_json": "Post (JSON):",
        "label_comments_json": "Comments (JSON):",
        "details_error": "Error loading details",
        "label_comment": "Comment:",
        "btn_add_comment": "Add comment",
        "comment_success": "Comment added.\nPost ID: {post_id}\n\nPost:\n{url}\n\nPost URL has been copied to clipboard.",
        "comment_success_title": "Success",
        "comment_error": "Error adding comment",
        "common_missing_post_id_or_content": "Post ID and comment text are required.",
        "common_missing_post_id": "Post ID is required.",
        "copy_dialog_copy": "Copy",
        "copy_dialog_ok": "OK",
        "copy_dialog_save": "Save…",
        "copy_dialog_title_json": "API response (JSON)",
        "copy_saved_msg": "File saved.",
        "copy_saved_error": "Error saving file.",
        "copy_or_open_title_post": "Post created",
        "copy_or_open_title_comment": "Comment added",
        "copy_or_open_question": "Link has been copied to clipboard:\n{url}\n\nOpen in browser?",
        "register_steps_title": "Registration instructions",
        "register_steps_header": "Agent registered. Follow these steps:",
        "register_steps_claim_url": "🔗 Claim URL:",
        "register_steps_profile_url": "👤 Agent profile:",
        "register_steps_heartbeat_url": "❤️ HEARTBEAT:",
        "register_steps_skill_url": "📄 skill.md:",
        "register_steps_package_url": "📦 package.json:",
        "register_steps_tweet_template": "🐦 Verification tweet template:",
        "register_steps_status": "Agent status: {status}",
        "register_steps_btn_open_claim": "Open Claim URL",
        "register_steps_btn_copy_claim": "Copy Claim URL",
        "register_steps_btn_open_profile": "Open profile",
        "register_steps_btn_copy_profile": "Copy profile link",
        "register_steps_btn_close": "Close",
    },
}


def show_json_dialog(parent, text: str, tr: dict):
    dlg = QDialog(parent)
    dlg.setWindowTitle(tr["copy_dialog_title_json"])
    dlg.resize(600, 350)

    layout = QVBoxLayout(dlg)

    editor = QTextEdit()
    editor.setReadOnly(True)
    editor.setPlainText(text)

    buttons = QDialogButtonBox()
    btn_copy = buttons.addButton(tr["copy_dialog_copy"], QDialogButtonBox.ButtonRole.ActionRole)
    btn_save = buttons.addButton(tr["copy_dialog_save"], QDialogButtonBox.ButtonRole.ActionRole)
    btn_ok = buttons.addButton(tr["copy_dialog_ok"], QDialogButtonBox.ButtonRole.AcceptRole)

    def copy_to_clipboard():
        QGuiApplication.clipboard().setText(text)

    def save_to_file():
        path, _ = QFileDialog.getSaveFileName(
            parent,
            tr["copy_dialog_save"],
            "moltbook_agent_registration.json",
            "JSON Files (*.json);;All Files (*.*)",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(parent, tr["copy_dialog_save"], tr["copy_saved_msg"])
        except Exception as e:
            QMessageBox.critical(parent, tr["copy_dialog_save"], f"{tr['copy_saved_error']}\n{e}")

    btn_copy.clicked.connect(copy_to_clipboard)
    btn_save.clicked.connect(save_to_file)
    btn_ok.clicked.connect(dlg.accept)

    layout.addWidget(editor)
    layout.addWidget(buttons)

    dlg.exec()


def show_text_dialog(parent, title: str, text: str):
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.resize(600, 400)

    layout = QVBoxLayout(dlg)

    editor = QTextEdit()
    editor.setReadOnly(False)
    editor.setPlainText(text)

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    buttons.accepted.connect(dlg.accept)

    layout.addWidget(editor)
    layout.addWidget(buttons)

    dlg.exec()


class RegistrationStepsDialog(QDialog):
    def __init__(self, parent, data: dict, tr: dict):
        super().__init__(parent)
        self.tr = tr
        self.setWindowTitle(tr["register_steps_title"])
        self.resize(700, 500)

        layout = QVBoxLayout(self)

        header = QLabel(tr["register_steps_header"])
        layout.addWidget(header)

        setup = data.get("setup", {})
        for key in sorted(setup.keys()):
            step = setup.get(key)
            if not isinstance(step, dict):
                continue
            title = step.get("action") or key
            details = step.get("details") or ""
            why = step.get("why") or step.get("message_template") or ""

            label = QLabel(f"⭐ <b>{title}</b><br>{details}")
            if why:
                label.setText(label.text() + f"<br><i>{why}</i>")
            label.setWordWrap(True)
            layout.addWidget(label)

        agent = data.get("agent", {}) if isinstance(data, dict) else {}
        claim_url = data.get("claim_url") or agent.get("claim_url")
        profile_url = agent.get("profile_url")
        skill_files = data.get("skill_files", {}) if isinstance(data, dict) else {}
        heartbeat_url = skill_files.get("heartbeat_md") or skill_files.get("heartbeat_url")
        skill_url = skill_files.get("skill_md")
        package_url = skill_files.get("package_json") or skill_files.get("package_url")
        tweet_template = data.get("tweet_template")
        status = data.get("status") or agent.get("status")

        def add_link_row(caption_key: str, url_value: str, open_label_key: str, copy_label_key: str):
            if not url_value:
                return
            row = QHBoxLayout()
            edit = QLineEdit(url_value)
            edit.setReadOnly(True)
            row.addWidget(QLabel(tr[caption_key]))
            row.addWidget(edit)

            btn_open = QPushButton(tr[open_label_key])
            btn_copy = QPushButton(tr[copy_label_key])

            def do_open():
                webbrowser.open(url_value)

            def do_copy():
                QGuiApplication.clipboard().setText(url_value)

            btn_open.clicked.connect(do_open)
            btn_copy.clicked.connect(do_copy)

            row.addWidget(btn_open)
            row.addWidget(btn_copy)
            layout.addLayout(row)

        add_link_row("register_steps_claim_url", claim_url, "register_steps_btn_open_claim", "register_steps_btn_copy_claim")
        add_link_row("register_steps_profile_url", profile_url, "register_steps_btn_open_profile", "register_steps_btn_copy_profile")

        if heartbeat_url:
            row = QHBoxLayout()
            edit = QLineEdit(heartbeat_url)
            edit.setReadOnly(True)
            row.addWidget(QLabel(tr["register_steps_heartbeat_url"]))
            row.addWidget(edit)
            layout.addLayout(row)

        if skill_url:
            row = QHBoxLayout()
            edit = QLineEdit(skill_url)
            edit.setReadOnly(True)
            row.addWidget(QLabel(tr["register_steps_skill_url"]))
            row.addWidget(edit)
            layout.addLayout(row)

        if package_url:
            row = QHBoxLayout()
            edit = QLineEdit(package_url)
            edit.setReadOnly(True)
            row.addWidget(QLabel(tr["register_steps_package_url"]))
            row.addWidget(edit)
            layout.addLayout(row)

        if tweet_template:
            lbl = QLabel(f"{tr['register_steps_tweet_template']}<br><code>{tweet_template}</code>")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        if status:
            layout.addWidget(QLabel(tr["register_steps_status"].format(status=status)))

        pretty_json = json.dumps(data, indent=2, ensure_ascii=False)
        btn_json = QPushButton(tr["copy_dialog_title_json"])

        def open_json_dialog():
            show_json_dialog(self, pretty_json, tr)

        btn_json.clicked.connect(open_json_dialog)
        layout.addWidget(btn_json)

        buttons = QDialogButtonBox()
        btn_close = buttons.addButton(tr["register_steps_btn_close"], QDialogButtonBox.ButtonRole.AcceptRole)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(buttons)


class MoldBookGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_lang = "pl"
        self.tr = TRANSLATIONS[self.current_lang]

        self.current_agent_name = None
        self.current_agent_profile_url = None

        self.setWindowTitle(self.tr["window_title"])
        self.resize(950, 650)

        main_layout = QVBoxLayout(self)

        lang_layout = QHBoxLayout()
        self.lang_label = QLabel(self.tr["label_lang"])
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Polski", "pl")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.currentIndexChanged.connect(self.change_language)

        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        main_layout.addLayout(lang_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._init_env_tab()
        self._init_register_tab()
        self._init_post_tab()
        self._init_feed_tab()
        self._init_post_details_tab()
        self._init_comment_tab()
        self._init_info_tab()

        self._try_load_agent_profile()

        self.tabs.setCurrentWidget(self.info_tab)

    def change_language(self, index: int):
        lang_code = self.lang_combo.itemData(index)
        if not lang_code:
            return
        self.current_lang = lang_code
        self.tr = TRANSLATIONS[self.current_lang]
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.tr["window_title"])
        self.lang_label.setText(self.tr["label_lang"])
        self.tabs.setTabText(0, self.tr["tab_env"])
        self.tabs.setTabText(1, self.tr["tab_register"])
        self.tabs.setTabText(2, self.tr["tab_post"])
        self.tabs.setTabText(3, self.tr["tab_feed"])
        self.tabs.setTabText(4, self.tr["tab_details"])
        self.tabs.setTabText(5, self.tr["tab_comment"])
        self.tabs.setTabText(6, self.tr["tab_info"])

        self.env_label.setText(self.tr["label_env"])
        self.env_save_btn.setText(self.tr["btn_env_save"])

        self.label_agent_name.setText(self.tr["label_agent_name"])
        self.label_agent_desc.setText(self.tr["label_agent_desc"])
        self.register_button.setText(self.tr["btn_register"])
        self.agent_info_title.setText(self.tr["label_agent_info"])

        self.label_submolt.setText(self.tr["label_submolt"])
        self.label_title.setText(self.tr["label_title"])
        self.label_content.setText(self.tr["label_content"])
        self.post_button.setText(self.tr["btn_post"])

        self.feed_sort_label.setText(self.tr["label_sort"])
        self.feed_limit_label.setText(self.tr["label_limit"])
        self.feed_refresh_btn.setText(self.tr["btn_refresh"])
        self.feed_posts_label.setText(self.tr["label_posts"])
        self.feed_json_label.setText(self.tr["label_json_response"])

        self.details_id_label.setText(self.tr["label_post_id"])
        self.details_load_btn.setText(self.tr["btn_load_details"])
        self.details_post_label.setText(self.tr["label_post_json"])
        self.details_comments_label.setText(self.tr["label_comments_json"])

        self.comment_id_label.setText(self.tr["label_post_id"])
        self.comment_content_label.setText(self.tr["label_comment"])
        self.comment_button.setText(self.tr["btn_add_comment"])

        self.info_text.setPlainText(INFO_TEXT_PL if self.current_lang == "pl" else INFO_TEXT_EN)

    def _try_load_agent_profile(self):
        try:
            profile = moltbook_client.get_my_profile()
            name = profile.get("username") or profile.get("name") or profile.get("agent_name")
            if not name:
                return
            self.current_agent_name = name
            self.current_agent_profile_url = moltbook_client.get_agent_profile_url(name)
            info = f"{self.current_agent_name}"
            if self.current_agent_profile_url:
                info += f"\n{self.current_agent_profile_url}"
            self.agent_info_value.setText(info)
        except Exception:
            pass

    def _init_env_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.env_label = QLabel(self.tr["label_env"])
        self.env_editor = QTextEdit()
        self.env_editor.setPlainText(env_editor.load_env())

        btn_layout = QHBoxLayout()
        self.env_save_btn = QPushButton(self.tr["btn_env_save"])
        self.env_save_btn.clicked.connect(self.save_env)
        btn_layout.addWidget(self.env_save_btn)
        btn_layout.addStretch()

        layout.addWidget(self.env_label)
        layout.addWidget(self.env_editor)
        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, self.tr["tab_env"])

    def save_env(self):
        try:
            raw = self.env_editor.toPlainText()
            env_editor.save_env(raw)
            QMessageBox.information(self, "OK", self.tr["msg_env_saved"])
            self._try_load_agent_profile()
        except Exception as e:
            QMessageBox.critical(self, self.tr["msg_env_error"], str(e))

    def _init_register_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        self.register_form = form

        self.reg_name = QLineEdit()
        self.reg_desc = QTextEdit()

        self.label_agent_name = QLabel(self.tr["label_agent_name"])
        self.label_agent_desc = QLabel(self.tr["label_agent_desc"])

        form.addRow(self.label_agent_name, self.reg_name)
        form.addRow(self.label_agent_desc, self.reg_desc)

        self.agent_info_title = QLabel(self.tr["label_agent_info"])
        self.agent_info_value = QLabel("")
        self.agent_info_value.setWordWrap(True)
        form.addRow(self.agent_info_title, self.agent_info_value)

        self.register_button = QPushButton(self.tr["btn_register"])
        self.register_button.clicked.connect(self.register_agent)
        form.addRow(self.register_button)

        self.tabs.addTab(tab, self.tr["tab_register"])

    def register_agent(self):
        try:
            name = self.reg_name.text().strip()
            description = self.reg_desc.toPlainText().strip()

            if not name or not description:
                raise ValueError(self.tr["register_name_required"])

            ok, data = register_moltbook.register_agent(
                name=name,
                description=description,
            )

            pretty_json = json.dumps(data, indent=2, ensure_ascii=False)

            agent = data.get("agent", {}) if isinstance(data, dict) else {}
            agent_id = agent.get("id") or (data.get("id") if isinstance(data, dict) else None)
            api_key = agent.get("api_key") if isinstance(agent, dict) else None

            if ok and api_key:
                env_editor.set_env_value("MOLTBOOK_API_KEY", api_key)
                try:
                    self.env_editor.setPlainText(env_editor.load_env())
                except Exception:
                    pass

                self._try_load_agent_profile()

                dlg = RegistrationStepsDialog(self, data, self.tr)
                dlg.exec()
                return

            if ok and not api_key:
                show_json_dialog(self, pretty_json, self.tr)
                return

            api_msg = ""
            if isinstance(data, dict):
                api_msg = data.get("message") or data.get("error") or pretty_json
            else:
                api_msg = pretty_json

            if agent_id:
                api_msg += f"\n\nID agenta (z odpowiedzi): {agent_id}"

            QMessageBox.warning(
                self,
                self.tr["register_conflict_title"],
                api_msg,
            )

        except Exception as e:
            QMessageBox.critical(self, self.tr["register_error"], str(e))

    def _init_post_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        self.post_form = form

        self.post_submolt = QLineEdit()
        self.post_submolt.setText(DEFAULT_SUBMOLT)

        self.post_title = QLineEdit()
        self.post_content = QTextEdit()

        self.label_submolt = QLabel(self.tr["label_submolt"])
        self.label_title = QLabel(self.tr["label_title"])
        self.label_content = QLabel(self.tr["label_content"])

        form.addRow(self.label_submolt, self.post_submolt)
        form.addRow(self.label_title, self.post_title)
        form.addRow(self.label_content, self.post_content)

        self.post_button = QPushButton(self.tr["btn_post"])
        self.post_button.clicked.connect(self.create_post)
        form.addRow(self.post_button)

        self.tabs.addTab(tab, self.tr["tab_post"])

    def _copy_or_open_url(self, url: str, title_key: str):
        QGuiApplication.clipboard().setText(url)
        reply = QMessageBox.question(
            self,
            self.tr[title_key],
            self.tr["copy_or_open_question"].format(url=url),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            webbrowser.open(url)

    def create_post(self):
        try:
            submolt = self.post_submolt.text().strip() or DEFAULT_SUBMOLT
            if submolt.startswith("m/"):
                submolt = submolt[2:]
            title = self.post_title.text().strip()
            content = self.post_content.toPlainText().strip()

            if not title or not content:
                raise ValueError(self.tr["label_title"] + " / " + self.tr["label_content"])

            resp = moltbook_client.post_to_moltbook(
                submolt=submolt,
                title=title,
                content=content,
            )

            post_id = resp.get("id")
            if not post_id:
                show_text_dialog(
                    self,
                    self.tr["post_success_title"],
                    json.dumps(resp, indent=2, ensure_ascii=False),
                )
                return

            post_url = moltbook_client.get_post_url(post_id)
            msg = self.tr["post_success_msg"].format(id=post_id, url=post_url)
            show_text_dialog(self, self.tr["post_success_title"], msg)
            self._copy_or_open_url(post_url, "copy_or_open_title_post")

        except Exception as e:
            QMessageBox.critical(self, self.tr["post_error"], str(e))

    def _init_feed_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        controls = QHBoxLayout()
        self.feed_sort_label = QLabel(self.tr["label_sort"])
        self.feed_sort = QComboBox()
        self.feed_sort.addItems(["hot", "new"])
        self.feed_limit_label = QLabel(self.tr["label_limit"])
        self.feed_limit = QLineEdit()
        self.feed_limit.setText("20")

        self.feed_refresh_btn = QPushButton(self.tr["btn_refresh"])
        self.feed_refresh_btn.clicked.connect(self.load_feed)

        controls.addWidget(self.feed_sort_label)
        controls.addWidget(self.feed_sort)
        controls.addWidget(self.feed_limit_label)
        controls.addWidget(self.feed_limit)
        controls.addWidget(self.feed_refresh_btn)
        controls.addStretch()

        self.feed_posts_label = QLabel(self.tr["label_posts"])
        self.feed_list = QListWidget()
        self.feed_json_label = QLabel(self.tr["label_json_response"])
        self.feed_raw = QTextEdit()
        self.feed_raw.setReadOnly(True)

        layout.addLayout(controls)
        layout.addWidget(self.feed_posts_label)
        layout.addWidget(self.feed_list)
        layout.addWidget(self.feed_json_label)
        layout.addWidget(self.feed_raw)

        self.feed_list.itemClicked.connect(self._on_feed_item_clicked)

        self.tabs.addTab(tab, self.tr["tab_feed"])

    def load_feed(self):
        try:
            sort = self.feed_sort.currentText()
            limit = int(self.feed_limit.text().strip() or "20")

            data = moltbook_client.list_posts(sort=sort, limit=limit)

            self.feed_raw.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))

            posts = data.get("posts", []) if isinstance(data, dict) else data

            self.feed_list.clear()

            for post in posts:
                if not isinstance(post, dict):
                    continue
                title = post.get("title", "(no title)")
                pid = post.get("id", "")
                sm = post.get("submolt")
                if isinstance(sm, dict):
                    submolt = sm.get("name", "")
                else:
                    submolt = sm or ""
                item = QListWidgetItem(f"[{submolt}] {title} ({pid})")
                item.setData(32, pid)
                self.feed_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, self.tr["feed_error"], str(e))

    def _on_feed_item_clicked(self, item: QListWidgetItem):
        pid = item.data(32)
        if pid:
            self.post_details_id.setText(pid)
            self.tabs.setCurrentWidget(self.post_details_tab)
            self.load_post_details()

    def _init_post_details_tab(self):
        tab = QWidget()
        self.post_details_tab = tab
        layout = QVBoxLayout(tab)

        form = QFormLayout()
        self.details_id_label = QLabel(self.tr["label_post_id"])
        self.post_details_id = QLineEdit()
        self.details_load_btn = QPushButton(self.tr["btn_load_details"])
        self.details_load_btn.clicked.connect(self.load_post_details)

        form.addRow(self.details_id_label, self.post_details_id)
        form.addRow(self.details_load_btn)

        self.details_post_label = QLabel(self.tr["label_post_json"])
        self.post_details_json = QTextEdit()
        self.post_details_json.setReadOnly(True)

        self.details_comments_label = QLabel(self.tr["label_comments_json"])
        self.post_comments_json = QTextEdit()
        self.post_comments_json.setReadOnly(True)

        layout.addLayout(form)
        layout.addWidget(self.details_post_label)
        layout.addWidget(self.post_details_json)
        layout.addWidget(self.details_comments_label)
        layout.addWidget(self.post_comments_json)

        self.tabs.addTab(tab, self.tr["tab_details"])

    def load_post_details(self):
        try:
            pid = self.post_details_id.text().strip()
            if not pid:
                raise ValueError(self.tr["common_missing_post_id"])

            post_data = moltbook_client.get_post(pid)
            comments_data = moltbook_client.get_post_comments(pid)

            self.post_details_json.setPlainText(
                json.dumps(post_data, indent=2, ensure_ascii=False)
            )
            self.post_comments_json.setPlainText(
                json.dumps(comments_data, indent=2, ensure_ascii=False)
            )
        except Exception as e:
            QMessageBox.critical(self, self.tr["details_error"], str(e))

    def _init_comment_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.comment_id_label = QLabel(self.tr["label_post_id"])
        self.comment_post_id = QLineEdit()
        self.comment_content_label = QLabel(self.tr["label_comment"])
        self.comment_content = QTextEdit()

        form.addRow(self.comment_id_label, self.comment_post_id)
        form.addRow(self.comment_content_label, self.comment_content)

        self.comment_button = QPushButton(self.tr["btn_add_comment"])
        self.comment_button.clicked.connect(self.comment_post)
        form.addRow(self.comment_button)

        self.tabs.addTab(tab, self.tr["tab_comment"])

    def comment_post(self):
        try:
            post_id = self.comment_post_id.text().strip()
            content = self.comment_content.toPlainText().strip()

            if not post_id or not content:
                raise ValueError(self.tr["common_missing_post_id_or_content"])

            resp = vote_client.add_comment(post_id=post_id, content=content)
            # comment_id = resp.get("id", "unknown")  # nie używamy

            post_url = moltbook_client.get_post_url(post_id)

            msg = self.tr["comment_success"].format(
                post_id=post_id,
                url=post_url,
            )
            show_text_dialog(self, self.tr["comment_success_title"], msg)
            self._copy_or_open_url(post_url, "copy_or_open_title_comment")

        except Exception as e:
            QMessageBox.critical(self, self.tr["comment_error"], str(e))

    def _init_info_tab(self):
        tab = QWidget()
        self.info_tab = tab
        layout = QVBoxLayout(tab)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(False)
        self.info_text.setPlainText(INFO_TEXT_PL if self.current_lang == "pl" else INFO_TEXT_EN)

        layout.addWidget(self.info_text)

        self.tabs.addTab(tab, self.tr["tab_info"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MoldBookGUI()
    win.show()
    sys.exit(app.exec())

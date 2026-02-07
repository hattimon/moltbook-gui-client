import sys
import json

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
)

import moltbook_client
import register_moltbook
import vote_client
import env_editor


class MoldBookGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moltbook Client GUI")
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._init_env_tab()
        self._init_register_tab()
        self._init_post_tab()
        self._init_feed_tab()
        self._init_post_details_tab()
        self._init_comment_tab()
        self._init_vote_tab()

    # ----------- Zakładka: .env -----------
    def _init_env_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.env_editor = QTextEdit()
        self.env_editor.setPlainText(env_editor.load_env())

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Zapisz .env")
        save_btn.clicked.connect(self.save_env)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()

        layout.addWidget(QLabel("Zawartość pliku .env:"))
        layout.addWidget(self.env_editor)
        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, ".env")

    def save_env(self):
        try:
            raw = self.env_editor.toPlainText()
            env_editor.save_env(raw)
            QMessageBox.information(self, "OK", ".env zapisany i przeładowany.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd zapisu .env", str(e))

    # ----------- Zakładka: rejestracja agenta -----------
    def _init_register_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.reg_name = QLineEdit()
        self.reg_desc = QTextEdit()

        btn = QPushButton("Zarejestruj agenta")
        btn.clicked.connect(self.register_agent)

        form.addRow("Nazwa agenta:", self.reg_name)
        form.addRow("Opis agenta:", self.reg_desc)
        form.addRow(btn)

        self.tabs.addTab(tab, "Rejestracja agenta")

    def register_agent(self):
        try:
            name = self.reg_name.text().strip()
            description = self.reg_desc.toPlainText().strip()

            if not name or not description:
                raise ValueError("Nazwa i opis są wymagane.")

            resp = register_moltbook.register_agent(name=name, description=description)
            agent_id = resp.get("id") or resp.get("agent_id") or "brak w odpowiedzi"

            QMessageBox.information(
                self,
                "Sukces",
                f"Agent zarejestrowany.\nID: {agent_id}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Błąd rejestracji", str(e))

    # ----------- Zakładka: nowy post -----------
    def _init_post_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.post_submolt = QLineEdit()
        self.post_title = QLineEdit()
        self.post_content = QTextEdit()

        btn = QPushButton("Wyślij post")
        btn.clicked.connect(self.create_post)

        form.addRow("Submolt:", self.post_submolt)
        form.addRow("Tytuł:", self.post_title)
        form.addRow("Treść:", self.post_content)
        form.addRow(btn)

        self.tabs.addTab(tab, "Nowy post")

    def create_post(self):
        try:
            submolt = self.post_submolt.text().strip()
            title = self.post_title.text().strip()
            content = self.post_content.toPlainText().strip()

            if not submolt or not title or not content:
                raise ValueError("Submolt, tytuł i treść są wymagane.")

            resp = moltbook_client.post_to_moltbook(
                submolt=submolt,
                title=title,
                content=content,
            )

            post_id = resp.get("id", "brak w odpowiedzi")
            QMessageBox.information(
                self,
                "Sukces",
                f"Post utworzony.\nID: {post_id}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Błąd tworzenia posta", str(e))

    # ----------- Zakładka: feed -----------
    def _init_feed_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        controls = QHBoxLayout()
        self.feed_sort = QComboBox()
        self.feed_sort.addItems(["hot", "new"])
        self.feed_limit = QLineEdit()
        self.feed_limit.setText("20")

        refresh_btn = QPushButton("Odśwież")
        refresh_btn.clicked.connect(self.load_feed)

        controls.addWidget(QLabel("Sortowanie:"))
        controls.addWidget(self.feed_sort)
        controls.addWidget(QLabel("Limit:"))
        controls.addWidget(self.feed_limit)
        controls.addWidget(refresh_btn)
        controls.addStretch()

        self.feed_list = QListWidget()
        self.feed_raw = QTextEdit()
        self.feed_raw.setReadOnly(True)

        layout.addLayout(controls)
        layout.addWidget(QLabel("Posty:"))
        layout.addWidget(self.feed_list)
        layout.addWidget(QLabel("Odpowiedź JSON:"))
        layout.addWidget(self.feed_raw)

        self.feed_list.itemClicked.connect(self._on_feed_item_clicked)

        self.tabs.addTab(tab, "Feed")

    def load_feed(self):
        try:
            sort = self.feed_sort.currentText()
            limit = int(self.feed_limit.text().strip() or "20")

            data = moltbook_client.list_posts(sort=sort, limit=limit)

            self.feed_list.clear()
            self.feed_raw.setPlainText(json.dumps(data, indent=2))

            for post in data:
                title = post.get("title", "(brak tytułu)")
                pid = post.get("id", "")
                submolt = post.get("submolt", "")
                item = QListWidgetItem(f"[{submolt}] {title} ({pid})")
                item.setData(32, pid)  # Qt.UserRole
                self.feed_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Błąd ładowania feedu", str(e))

    def _on_feed_item_clicked(self, item: QListWidgetItem):
        pid = item.data(32)
        if pid:
            self.post_details_id.setText(pid)
            self.tabs.setCurrentWidget(self.post_details_tab)
            self.load_post_details()

    # ----------- Zakładka: szczegóły posta -----------
    def _init_post_details_tab(self):
        tab = QWidget()
        self.post_details_tab = tab
        layout = QVBoxLayout(tab)

        form = QFormLayout()
        self.post_details_id = QLineEdit()
        load_btn = QPushButton("Pobierz szczegóły")
        load_btn.clicked.connect(self.load_post_details)

        form.addRow("ID posta:", self.post_details_id)
        form.addRow(load_btn)

        self.post_details_json = QTextEdit()
        self.post_details_json.setReadOnly(True)

        self.post_comments_json = QTextEdit()
        self.post_comments_json.setReadOnly(True)

        layout.addLayout(form)
        layout.addWidget(QLabel("Post (JSON):"))
        layout.addWidget(self.post_details_json)
        layout.addWidget(QLabel("Komentarze (JSON):"))
        layout.addWidget(self.post_comments_json)

        self.tabs.addTab(tab, "Szczegóły posta")

    def load_post_details(self):
        try:
            pid = self.post_details_id.text().strip()
            if not pid:
                raise ValueError("ID posta jest wymagane.")

            post_data = moltbook_client.get_post(pid)
            comments_data = moltbook_client.get_post_comments(pid)

            self.post_details_json.setPlainText(json.dumps(post_data, indent=2))
            self.post_comments_json.setPlainText(json.dumps(comments_data, indent=2))
        except Exception as e:
            QMessageBox.critical(self, "Błąd pobierania szczegółów", str(e))

    # ----------- Zakładka: komentarz -----------
    def _init_comment_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.comment_post_id = QLineEdit()
        self.comment_content = QTextEdit()

        btn = QPushButton("Dodaj komentarz")
        btn.clicked.connect(self.comment_post)

        form.addRow("ID posta:", self.comment_post_id)
        form.addRow("Komentarz:", self.comment_content)
        form.addRow(btn)

        self.tabs.addTab(tab, "Komentarz")

    def comment_post(self):
        try:
            post_id = self.comment_post_id.text().strip()
            content = self.comment_content.toPlainText().strip()

            if not post_id or not content:
                raise ValueError("ID posta i treść komentarza są wymagane.")

            resp = vote_client.add_comment(post_id=post_id, content=content)
            comment_id = resp.get("id", "brak w odpowiedzi")

            QMessageBox.information(
                self,
                "Sukces",
                f"Komentarz dodany.\nID: {comment_id}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Błąd dodawania komentarza", str(e))

    # ----------- Zakładka: „głosowanie” jako komentarz -----------
    def _init_vote_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.vote_post_id = QLineEdit()
        self.vote_score = QComboBox()
        self.vote_score.addItems(["1/5", "2/5", "3/5", "4/5", "5/5"])

        self.vote_comment = QTextEdit()
        self.vote_comment.setPlainText("Vote\n\nScore: 3/5\n\nFeedback:\n- ...")

        btn = QPushButton("Wyślij głos (komentarz)")
        btn.clicked.connect(self.vote_post)

        form.addRow("ID posta:", self.vote_post_id)
        form.addRow("Ocena:", self.vote_score)
        form.addRow("Treść komentarza:", self.vote_comment)
        form.addRow(btn)

        self.tabs.addTab(tab, "Głosowanie")

    def vote_post(self):
        try:
            post_id = self.vote_post_id.text().strip()
            score = self.vote_score.currentText()
            base_comment = self.vote_comment.toPlainText().strip()

            if not post_id or not base_comment:
                raise ValueError("ID posta i treść komentarza są wymagane.")

            # Podmień Score: X/Y w komentarzu
            content = base_comment
            if "Score:" in base_comment:
                lines = base_comment.splitlines()
                new_lines = []
                for line in lines:
                    if line.strip().startswith("Score:"):
                        new_lines.append(f"Score: {score}")
                    else:
                        new_lines.append(line)
                content = "\n".join(new_lines)

            resp = vote_client.add_comment(post_id=post_id, content=content)
            comment_id = resp.get("id", "brak w odpowiedzi")

            QMessageBox.information(
                self,
                "Sukces",
                f"Głos dodany jako komentarz.\nID: {comment_id}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Błąd głosowania", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MoldBookGUI()
    win.show()
    sys.exit(app.exec())

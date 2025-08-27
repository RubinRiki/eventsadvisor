from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from ui.components.cards import Card
from ui.components.labels import PageTitle, SectionTitle, Muted


class DetailsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)

        root.addWidget(PageTitle("שם אירוע · דמו"))
        root.addWidget(Muted("מיקום: היכל התרבות • תל אביב · תאריך: 15/10/2025 · מחיר החל מ-₪180"))

        info = Card(); il = QVBoxLayout(info); il.setContentsMargins(16,16,16,16); il.setSpacing(8)
        il.addWidget(SectionTitle("על האירוע"))
        il.addWidget(Muted("תיאור קצר של האירוע… טקסט דמו לעיצוב."))
        root.addWidget(info)

        cta_row = QHBoxLayout()
        buy = QPushButton("המשך להזמנה"); buy.setObjectName("Primary")
        share = QPushButton("שתף"); share.setObjectName("Secondary")
        cta_row.addWidget(buy); cta_row.addWidget(share); cta_row.addStretch(1)
        root.addLayout(cta_row)
# בראש הקובץ אין שינויי import
class DetailsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self); root.setContentsMargins(16,28,16,16); root.setSpacing(12)

        self.title = PageTitle("שם אירוע · דמו")
        self.meta  = Muted("מיקום/תאריך/מחיר…")
        root.addWidget(self.title)
        root.addWidget(self.meta)

        info = Card(); il = QVBoxLayout(info); il.setContentsMargins(16,16,16,16); il.setSpacing(8)
        il.addWidget(SectionTitle("על האירוע"))
        self.desc = Muted("תיאור קצר של האירוע…")
        il.addWidget(self.desc)
        root.addWidget(info)

        cta_row = QHBoxLayout()
        buy = QPushButton("המשך להזמנה"); buy.setObjectName("Primary")
        share = QPushButton("שתף"); share.setObjectName("Secondary")
        cta_row.addWidget(buy); cta_row.addWidget(share); cta_row.addStretch(1)
        root.addLayout(cta_row)

    def set_event(self, title: str, meta: str, description: str):
        self.title.setText(title)
        self.meta.setText(meta)
        self.desc.setText(description)

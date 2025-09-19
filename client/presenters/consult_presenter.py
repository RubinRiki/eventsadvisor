# -*- coding: utf-8 -*-
# Consult Presenter: שואל את ה-AI (תשובה מלאה או סטרימינג חלקי אם תוסיפי בהמשך)
from PySide6.QtCore import QObject, Signal, Slot, QThread

class _AskWorker(QObject):
    answer = Signal(str)
    error  = Signal(str)
    def __init__(self, svc, question: str):
        super().__init__(); self.svc, self.q = svc, question
    def run(self):
        try:
            text = self.svc.ask(self.q)  # תשובה מלאה; אפשר להחליף ל-stream בעתיד
            self.answer.emit(text or "")
        except Exception as ex:
            self.error.emit(str(ex))

class ConsultPresenter(QObject):
    started = Signal()
    answer  = Signal(str)
    error   = Signal(str)
    done    = Signal()

    def __init__(self, ai_service):
        super().__init__()
        self.svc = ai_service
        self._t = None
        self._w = None

    @Slot(str)
    def ask(self, question: str):
        if self._t: return
        self.started.emit()
        self._t = QThread()
        self._w = _AskWorker(self.svc, question)
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.answer.connect(self.answer)
        self._w.error.connect(self.error)
        self._w.answer.connect(self._cleanup)
        self._w.error.connect(self._cleanup)
        self._t.start()

    def _cleanup(self):
        try:
            if self._t:
                self._t.quit(); self._t.wait()
        finally:
            self._t = None; self._w = None
        self.done.emit()

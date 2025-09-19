# -*- coding: utf-8 -*-
# Charts Presenter: מביא summary (totals/by_month/top_events)
from PySide6.QtCore import QObject, Signal, Slot, QThread

class _SummaryWorker(QObject):
    done  = Signal(dict)
    error = Signal(str)
    def __init__(self, svc):
        super().__init__(); self.svc = svc
    def run(self):
        try:
            data = self.svc.summary() or {}
            # הגנות מינוריות כדי להתאים לרינדור
            data.setdefault("totals", {})
            data.setdefault("by_month", [])
            data.setdefault("top_events", [])
            self.done.emit(data)
        except Exception as ex:
            self.error.emit(str(ex))

class ChartsPresenter(QObject):
    started   = Signal()
    dataReady = Signal(dict)
    error     = Signal(str)

    def __init__(self, analytics_service):
        super().__init__()
        self.svc = analytics_service
        self._t = None
        self._w = None

    @Slot()
    def load(self):
        if self._t: return
        self.started.emit()
        self._t = QThread()
        self._w = _SummaryWorker(self.svc)
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.done.connect(self.dataReady)
        self._w.error.connect(self.error)
        self._w.done.connect(self._cleanup)
        self._w.error.connect(self._cleanup)
        self._t.start()

    def _cleanup(self):
        try:
            if self._t:
                self._t.quit(); self._t.wait()
        finally:
            self._t = None; self._w = None

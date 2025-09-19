# client/presenters/search_presenter.py
from PySide6.QtCore import QObject, Signal, Slot, QThread

class _SearchWorker(QObject):
    done = Signal(list); error = Signal(str)
    def __init__(self, svc, q, params): super().__init__(); self.svc, self.q, self.params = svc,q,params
    def run(self):
        try: self.done.emit(self.svc.search(self.q, **(self.params or {})))
        except Exception as ex: self.error.emit(str(ex))

class SearchPresenter(QObject):
    started = Signal(); dataReady = Signal(list); error = Signal(str)
    def __init__(self, service): super().__init__(); self.svc=service; self._t=None; self._w=None
    @Slot(str, dict)
    def load(self, q="", params=None):
        if self._t: return
        self.started.emit(); self._t=QThread(); self._w=_SearchWorker(self.svc, q, params)
        self._w.moveToThread(self._t); self._t.started.connect(self._w.run)
        self._w.done.connect(self.dataReady); self._w.error.connect(self.error)
        self._w.done.connect(self._cleanup); self._w.error.connect(self._cleanup); self._t.start()
    def _cleanup(self): self._t.quit(); self._t.wait(); self._t=None; self._w=None

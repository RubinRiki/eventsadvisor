# -*- coding: utf-8 -*-
# Details Presenter: טוען אירוע + מנהל Like/Unlike, ללא תלות ב-Qt Widgets
from PySide6.QtCore import QObject, Signal, Slot, QThread

class _LoadEventWorker(QObject):
    done  = Signal(dict)
    error = Signal(str)
    def __init__(self, svc, event_id):
        super().__init__(); self.svc, self.event_id = svc, int(event_id)
    def run(self):
        try:
            data = self.svc.get_event(self.event_id)
            self.done.emit(data)
        except Exception as ex:
            self.error.emit(str(ex))

class _LikeStateWorker(QObject):
    done  = Signal(bool)   # liked?
    error = Signal(str)
    def __init__(self, svc, event_id):
        super().__init__(); self.svc, self.event_id = svc, int(event_id)
    def run(self):
        try:
            liked = self.svc.is_liked(self.event_id)
            self.done.emit(bool(liked))
        except Exception as ex:
            self.error.emit(str(ex))

class _LikeWorker(QObject):
    done  = Signal()
    error = Signal(str)
    def __init__(self, svc, event_id, do_like: bool):
        super().__init__(); self.svc, self.event_id, self.do_like = svc, int(event_id), do_like
    def run(self):
        try:
            (self.svc.like if self.do_like else self.svc.unlike)(self.event_id)
            self.done.emit()
        except Exception as ex:
            self.error.emit(str(ex))

class DetailsPresenter(QObject):
    started    = Signal()
    eventReady = Signal(dict)
    likeState  = Signal(bool)   # True=liked, False=unliked
    error      = Signal(str)

    def __init__(self, events_service):
        super().__init__()
        self.svc = events_service
        self._t = None
        self._w = None
        self._event_id = None

    @Slot(int)
    def load(self, event_id: int):
        if self._t: return
        self.started.emit()
        self._event_id = int(event_id)
        self._t = QThread()
        self._w = _LoadEventWorker(self.svc, self._event_id)
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.done.connect(self.eventReady)
        self._w.error.connect(self.error)
        self._w.done.connect(self._cleanup)
        self._w.error.connect(self._cleanup)
        self._t.start()

    @Slot()
    def init_like_state(self):
        if not self._event_id or self._t: return
        self._t = QThread()
        self._w = _LikeStateWorker(self.svc, self._event_id)
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.done.connect(self.likeState)
        self._w.error.connect(self._like_err)
        self._w.done.connect(self._cleanup)
        self._w.error.connect(self._cleanup)
        self._t.start()

    @Slot(bool)
    def toggle_like(self, currently_liked: bool):
        if not self._event_id or self._t: return
        self._t = QThread()
        self._w = _LikeWorker(self.svc, self._event_id, do_like=not currently_liked)
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.done.connect(lambda: self.likeState.emit(not currently_liked))
        self._w.error.connect(self.error)
        self._w.done.connect(self._cleanup)
        self._w.error.connect(self._cleanup)
        self._t.start()

    def _like_err(self, _msg: str):
        # אם נכשל — נחזיר false כמצב ברירת מחדל
        self.likeState.emit(False)

    def _cleanup(self):
        try:
            if self._t:
                self._t.quit()
                self._t.wait()
        finally:
            self._t = None
            self._w = None

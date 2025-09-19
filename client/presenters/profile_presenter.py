# -*- coding: utf-8 -*-
# Profile Presenter: טוען me() ולייקים; תומך בעדכון שם/סיסמה
from PySide6.QtCore import QObject, Signal, Slot, QThread

class _LoadProfileWorker(QObject):
    done  = Signal(dict)
    error = Signal(str)
    def __init__(self, svc):
        super().__init__(); self.svc = svc
    def run(self):
        try:
            me    = self.svc.me()
            likes = self.svc.my_likes()
            self.done.emit({"me": me, "likes": likes})
        except Exception as ex:
            self.error.emit(str(ex))

class _PatchUserWorker(QObject):
    done  = Signal()
    error = Signal(str)
    def __init__(self, svc, payload):
        super().__init__(); self.svc, self.payload = svc, payload
    def run(self):
        try:
            self.svc.patch_me(**(self.payload or {}))
            self.done.emit()
        except Exception as ex:
            self.error.emit(str(ex))

class _ChangePasswordWorker(QObject):
    done  = Signal()
    error = Signal(str)
    def __init__(self, svc, password: str):
        super().__init__(); self.svc, self.password = svc, password
    def run(self):
        try:
            self.svc.change_password(self.password)
            self.done.emit()
        except Exception as ex:
            self.error.emit(str(ex))

class ProfilePresenter(QObject):
    started   = Signal()
    dataReady = Signal(dict)  # {"me":..., "likes":[...]}
    saved     = Signal()
    error     = Signal(str)

    def __init__(self, users_service):
        super().__init__()
        self.svc = users_service
        self._t = None
        self._w = None

    @Slot()
    def load(self):
        if self._t: return
        self.started.emit()
        self._t = QThread()
        self._w = _LoadProfileWorker(self.svc)
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.done.connect(self.dataReady)
        self._w.error.connect(self.error)
        self._w.done.connect(self._cleanup)
        self._w.error.connect(self._cleanup)
        self._t.start()

    @Slot(str)
    def update_username(self, username: str):
        if self._t: return
        self._t = QThread()
        self._w = _PatchUserWorker(self.svc, {"username": username})
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.done.connect(self.saved)
        self._w.error.connect(self.error)
        self._w.done.connect(self._cleanup)
        self._w.error.connect(self._cleanup)
        self._t.start()

    @Slot(str)
    def change_password(self, password: str):
        if self._t: return
        self._t = QThread()
        self._w = _ChangePasswordWorker(self.svc, password)
        self._w.moveToThread(self._t)
        self._t.started.connect(self._w.run)
        self._w.done.connect(self.saved)
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

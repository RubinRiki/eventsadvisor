# client/presenters/auth_presenter.py
from PySide6.QtCore import QObject, Signal, Slot, QThread

class _LoginWorker(QObject):
    done = Signal(dict); error = Signal(str)
    def __init__(self, svc, email, pwd): super().__init__(); self.svc, self.email, self.pwd = svc, email, pwd
    def run(self):
        try: self.done.emit(self.svc.login(self.email, self.pwd))
        except Exception as ex: self.error.emit(str(ex))

class _RegisterWorker(QObject):
    done = Signal(dict); error = Signal(str)
    def __init__(self, svc, u,e,p): super().__init__(); self.svc, self.u,self.e,self.p = svc,u,e,p
    def run(self):
        try: self.done.emit(self.svc.register(self.u,self.e,self.p))
        except Exception as ex: self.error.emit(str(ex))

class AuthPresenter(QObject):
    started = Signal(); loggedIn = Signal(str); registered = Signal(); error = Signal(str)
    def __init__(self, service): super().__init__(); self.svc=service; self._t=None; self._w=None
    @Slot(str,str)
    def login(self, email, pwd):
        if self._t: return
        self.started.emit(); self._t=QThread(); self._w=_LoginWorker(self.svc,email,pwd)
        self._w.moveToThread(self._t); self._t.started.connect(self._w.run)
        self._w.done.connect(self._on_login_ok); self._w.error.connect(self.error); self._w.done.connect(self._cleanup); self._w.error.connect(self._cleanup)
        self._t.start()
    def _on_login_ok(self, js): self.loggedIn.emit(js.get("access_token",""))
    @Slot(str,str,str)
    def register(self,u,e,p):
        if self._t: return
        self.started.emit(); self._t=QThread(); self._w=_RegisterWorker(self.svc,u,e,p)
        self._w.moveToThread(self._t); self._t.started.connect(self._w.run)
        self._w.done.connect(lambda _ : self.registered.emit()); self._w.error.connect(self.error); self._w.done.connect(self._cleanup); self._w.error.connect(self._cleanup)
        self._t.start()
    def _cleanup(self): self._t.quit(); self._t.wait(); self._t=None; self._w=None

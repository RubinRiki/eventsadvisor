# -*- coding: utf-8 -*-
# ================================================================
#  EventHub Client — app.py
#  Created by: Riki Rubin & Hadas Donat
# ================================================================
"""
📌 Purpose (Explanation Box)
Main entry point of the EventHub desktop client (PySide6).

Run from project root:
    python -m client.app
"""

import sys
from PySide6.QtWidgets import QApplication

# ✅ Relative import so `python -m client.app` works reliably
from .app_shell import AppShell
from .core.theme.style_manager import apply_styles 


def main() -> int:
    """Bootstraps the Qt application and launches the main shell window."""
    app = QApplication(sys.argv)   # create Qt application (event loop manager)
    apply_styles(app)    
    win = AppShell(app)            # create main window (shell)
    win.show()                     # show window
    return app.exec()              # start event loop


if __name__ == "__main__":
    sys.exit(main())

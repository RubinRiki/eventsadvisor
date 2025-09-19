from fastapi import background
from .palette import Palette as P, Radii as R

BASE_QSS = f"""
* {{
  color: #f5f5f5; /* טקסט בהיר יותר */
  font-family: "Inter","Rubik","Segoe UI",Arial;
  font-size: 16px; /* טקסט גדול יותר */
}}
QWidget {{ background:{P.bg}; }}
QScrollArea {{ border:none; background:transparent; }}

/* ----- כרטיסים ----- */
QFrame#Card {{
  background:{P.surface};
  border:1px solid {P.border};
  border-radius:{R.md}px;
  padding:12px;
}}

/* ----- כפתורים ----- */
QPushButton#Primary {{
  background:{P.accent};
  color:#111;
  border:none;
  border-radius:{R.sm}px;
  padding:12px 20px;
  font-weight:800;
}}
QPushButton#Primary:hover {{ background:#ffdf4d; }}

QPushButton#Secondary {{
  background:#2f374f;  /* הרבה יותר בהיר */
  color:#f5f5f5;
  border:1px solid {P.border};
  border-radius:{R.sm}px;
  padding:12px 20px;
  font-weight:700;
}}
QPushButton#Secondary:hover {{ background:{P.muted}; }}

QPushButton#Ghost {{
  background:transparent;
  color:#f5f5f5;
  border:1px dashed {P.border};
  border-radius:{R.sm}px;
  padding:12px 20px;
}}

/* ----- Inputs ----- */
QLineEdit,QComboBox,QDateEdit {{
  background:{P.elevated};
  border:1px solid {P.border};
  border-radius:{R.xs}px;
  padding:10px 12px;
  selection-background-color:{P.accent2};
}}
QLineEdit:focus,QComboBox:focus,QDateEdit:focus {{
  border:1px solid {P.accent2};
}}

/* DropDown של ComboBox */
QComboBox QAbstractItemView {{
  background:{P.surface};
  color:#f5f5f5;
  border:1px solid {P.border};
  selection-background-color:{P.accent2};
  padding:8px;
}}

/* ----- Pills / tags ----- */
QLabel#Pill {{
  background:#20283a;
  color:{P.muted};
  border:1px solid {P.border};
  border-radius:999px;
  padding:6px 12px;
  font-weight:700;
}}

/* ----- Sidebar ----- */
QWidget#Sidebar {{
  background:{P.surface};
  border-right:1px solid {P.border};
  padding-top:20px; /* מרווח מלמעלה */
}}
QPushButton#SideItem {{
  text-align:right; /* יישור לימין */
  padding:12px 16px;
  margin:6px 8px;
  background:transparent;
  border-radius:{R.sm}px;
  border:1px solid transparent;
  font-weight:700;
  font-size:16px;
}}
QPushButton#SideItem:hover {{
  background:#1f2533;
  border-color:{P.border};
}}
QPushButton#SideItem[current="true"] {{
  background:{P.accent};
  color:#111;
}}

/* ----- Tabs ----- */
QTabWidget#AuthTabs::pane {{
    border: 1px solid {P.border};
    border-radius: {R.md}px;
    background: {P.surface};
    margin-top: 8px;
}}

/* טאבים – ברירת מחדל */
QTabWidget#AuthTabs QTabBar::tab {{
    color: {P.muted};
    background: transparent;
    padding: 8px 16px;
    margin: 0 6px;
    border: 1px solid transparent;
    border-top-left-radius: {R.sm}px;
    border-top-right-radius: {R.sm}px;
}}

/* Hover */
QTabWidget#AuthTabs QTabBar::tab:hover {{
    color: {P.text};
    background: #1f2533;
}}

/* נבחר – עיצוב כמו QPushButton#Primary */
QTabWidget#AuthTabs QTabBar::tab:selected {{
    background: {P.accent};
    color: #111;
    border: none;
    border-radius: {R.sm}px;
    padding: 12px 20px;
    font-weight: 800;
}}

"""

def apply_styles(app):
    app.setStyleSheet(BASE_QSS)

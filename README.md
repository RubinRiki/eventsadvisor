# EventAdvisor – סיכום קצר לשותפה

## הנושא שבחרנו

אפליקציית Desktop למציאת **הופעות/אירועים**: חיפוש מהיר, צפייה בפרטים, שמירה למעקב, ובהמשך התראות ויועץ AI — הכול בחלון אחד עם מבנה קבוע.

## פונקציונליות מתוכננת (תמצית)

* חיפוש לפי **מילת מפתח / עיר / (בהמשך) טווח תאריכים**.
* רשימת תוצאות עקבית + פתיחת **קישור רשמי** לאירוע.
* **Wishlist/מעקב** לאירועים מועדפים (שמירה מקומית בשלב ראשון).
* **התראות** (סימולציה) על אירועים שמורים.
* **יועץ AI** דרך שכבת Gateway (שאלות טבעיות והצעות חלופיות).
* **גרפים** (QtCharts) – פילוח לפי ז׳אנר/עיר/זמן.
* **Auth בסיסי** (דמו) לשמירת מעקב פר‑משתמש.

### עומד בדרישות הפרויקט

* Desktop GUI ב‑**PySide6** (חלון יחיד, אותה חלוקה לאזורים; רק ה‑widgets המרכזיים מתחלפים).
* שרת **FastAPI** עם נקודות קצה ברורות.
* חיבור לשירות חיצוני (Ticketmaster / SeatGeek) דרך **Gateway**.
* (בהמשך) גרפים, יועץ AI, ופריסה/אחסון בענן לפי הצורך.

## טכנולוגיות ותלויות שהותקנו

* Python 3.11, **FastAPI**, **Uvicorn\[standard]**, **PySide6**, **httpx**, **pydantic**, **python‑dotenv**.
* מבנה תקיות עיקרי:

```
client/ (GUI)
server/
  api/events.py
  main.py
gateway/
  adapters/ (ממשקי צד שלישי, יתחבר בהמשך)
```

## מה כבר מומש (מאוד קצר)

* `GET /health` – בדיקת חיים.
* `GET /events/search` – מחזיר דמו כשאין `TM_API_KEY`; צריל להגדיר מפתח שיפנה , יפנה ל‑Ticketmaster.
* GUI: חלון **EventAdvisor** עם שדה חיפוש וכפתור שמציג תוצאות הדמו.
* קוד הספרים הוסר מהשרת.

## איך להריץ מקומית (Windows/PowerShell)

1. לפתוח PowerShell בתיקיית הפרויקט:

```powershell
py -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. להריץ שרת (לשונית 1):

```powershell
python -m uvicorn server.main:app --reload --port 8000
```

3. להריץ GUI (לשונית 2):

```powershell
.\venv\Scripts\Activate.ps1
python client\main.py
```

4. בדיקות: `http://127.0.0.1:8000/health` → `{ "ok": true }`  |  `http://127.0.0.1:8000/events/search` → דמו.

## להקמה בצד שלך (מאפס)

```powershell
git clone <repo-url>
cd <repo-folder>
py -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
# (אופציונלי) אם רוצים תוצאות אמת:
$env:TM_API_KEY = "<ticketmaster-key>"
python -m uvicorn server.main:app --reload --port 8000
python client\main.py
```

## תקלות נפוצות (שורה לכל תקלה)

* **ExecutionPolicy**: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` ואז הפעלה.
* **uvicorn לא מזוהה**: להריץ כ‑`python -m uvicorn ...`.
* **ModuleNotFoundError (PySide6/httpx)**: להריץ `pip install` בתוך ה‑venv הפעיל.
* **יצירת קבצים מרובי שורות ב‑PS**: לפתוח עם `notepad path\to\file.py` ולהדביק ידנית.

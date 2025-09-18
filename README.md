📘 README — EventHub (Final Project: Windows Systems Engineering)
🎯 תיאור הפרויקט

EventHub היא מערכת ניהול והצגת אירועים מבוססת ארכיטקטורה מודרנית:

Client (Desktop App) – ממשק משתמש גרפי (GUI) ב־PySide6, עיצוב מודרני עם QtCharts ו־Style Manager מותאם.

Gateway (BFF Layer) – מתווך קריאות בין הלקוח לשרת, מאובטח ותומך בהעברת headers/authorization.

Server (FastAPI + SQL Server) – שכבת backend המממשת REST API עם ניהול משתמשים, חיפוש אירועים, פרטי אירוע וסטטיסטיקות.

DB (Somee + SQL Server) – שמירת נתונים בענן, כולל views לסטטיסטיקות.

המערכת תומכת:

🔑 אוטנטיקציה (Register/Login עם JWT).

🔍 חיפוש אירועים עם סינון ו־paging.

📄 פרטי אירוע בודד.

📊 אנליטיקות וסטטיסטיקות (לפי חודשים/קטגוריות/אירועים).

🎨 UI מודרני עם תמיכה בריבוי מסכים (חיפוש, פרטים, דוחות).

🗂️ מבנה פרויקט
eventsadvisor/
│
├── client/                # אפליקציית Desktop (PySide6)
│   ├── app.py             # Entry point (main window)
│   ├── views/             # מסכים: SearchView, DetailsView, ChartsView
│   └── ui/                # קומפוננטות UI משותפות + Style Manager
│
├── gateway/               # BFF Gateway (FastAPI)
│   └── api/events.py      # Proxy endpoints לאירועים
│
├── server/                # FastAPI backend
│   ├── api/               # Routers (events, auth, analytics)
│   ├── models/            # מודלים (User, Event, Analytics)
│   ├── repositories/      # גישה ל־DB
│   ├── core/              # אבטחה, JWT, deps
│   └── infra/db.py        # חיבור למסד נתונים
│
└── requirements.txt       # תלות Python

▶️ הוראות הרצה

שכבת שרת (API Server)

cd eventsadvisor
uvicorn server.main:app --reload --port 8000


יעלה את ה־FastAPI ב־http://127.0.0.1:8000/docs

שכבת Gateway

uvicorn gateway.main:app --reload --port 9000


יאזין לקריאות מהלקוח.

שכבת לקוח (Desktop Client)

python -m client.app


יפתח חלון ראשי (SearchView כברירת מחדל, בעתיד אחרי Login).

✅ מה מוכן

✔️ Register/Login עם JWT עובד.

✔️ חיפוש אירועים כולל סינון (עיר, תאריכים, טקסט חופשי).

✔️ פרטי אירוע נטענים מה־Gateway ל־DetailsView.

✔️ סטטיסטיקות (טבלאות/גרפים) מתחברות לנתוני DB (באמצעות views).

✔️ עיצוב UI אחיד לפי Style Manager (palette + qss).

✔️ הפרדה ארכיטקטונית מלאה: Client ↔ Gateway ↔ Server ↔ DB.

🚧 מה עוד חסר / לשיפור

🔲 Login flow ב־Client – כרגע ה־App נפתח ישירות ל־SearchView. נדרש להוסיף חלון Login.

🔲 טעינת נתוני סטטיסטיקה – כרגע קיימים נתוני בסיס מה־views, צריך לשפר aggregation/דוחות להצגה יותר אינטואיטיבית.

🔲 טיפול בשגיאות/טעינה – חלק מהקריאות חסרות Loader/Spinner בצד הלקוח.

🔲 AI / RAG Integration – סעיף אופציונלי מהדרישות (התייעצות עם סוכן מבוסס Ollama/LLM) עדיין לא מומש.

🔲 הזמנות/קנייה – כפתור “המשך להזמנה” ב־DetailsView עדיין דמו, לא מחובר ללוגיקה.
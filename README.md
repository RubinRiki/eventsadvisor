# נייצר קובץ README.md עם התוכן שסיכמנו

readme_content = """# EventAdvisor – פרויקט סיום בהנדסת מערכות חלונות

## 🎯 תיאור כללי
מערכת לניהול וחיפוש אירועים, עם שמירת נתונים בענן וחיבור לשירות חיצוני.  
המערכת כוללת:
- **שרת אפליקציה (FastAPI)**  
- **בסיס נתונים בענן (Somee – SQL Server)**  
- **Gateway חיצוני (Ticketmaster / דמו)**  
- **אימות והרשאות עם JWT**  
- **ממשק משתמש (PySide6 + QtCharts)**

המערכת תומכת בחיפוש אירועים, הצגת פרטים, ניתוח נתונים בגרפים, הזמנות משתמשים, ושילוב נתונים ממקור חיצוני.

---

## ✅ מה עובד היום
- **ניהול משתמשים ואימות (Auth)**  
  - רישום משתמש חדש (`/auth/register`)  
  - התחברות (`/auth/login`) → קבלת `access_token`  
  - שליפת משתמש נוכחי (`/auth/me`) עם Bearer Token  

- **אירועים – DB פנימי (Somee)**  
  - `GET /events/search` → חיפוש עם סינון לפי טקסט, קטגוריה, תאריכים, ופאג’ינציה.  
  - `GET /events/{id}` → שליפת אירוע בודד.  
  - `GET /events/analytics/summary` → אנליטיקות לפי חודש/קטגוריה (מוגן בטוקן).  
  - טבלת Events עודכנה: שדות `Category`, `Price DECIMAL`, אינדקסים על `Date` ו־`Category`.

- **אירועים – Gateway חיצוני**  
  - `GET /tm/events/search` → תוצאות דמו/חיצוני (לדוגמה: Imagine Dragons).  
  - משמש להדגמת שילוב נתונים חיצוניים (דרישת Gateway).

- **Postman** – נבדקו תסריטים:  
  - Register/Login/Me  
  - Events: search / get  
  - Analytics (עם Bearer)  
  - Gateway search  

- **DB** – מוזן בנתוני דמו (5 אירועים: Conference, Music, Festival, Meetup, Workshop) לצורך בדיקות.

---

## 📐 ארכיטקטורה
- **FastAPI** – שרת REST עם ארגון לפי תבנית MVC/CQRS.  
- **Repositories** – גישה ל־DB עם `pyodbc`.  
- **Somee (SQL Server)** – אחסון טבלאות Users, Events, Orders.  
- **Gateway** – מודול נפרד לשירות חיצוני תחת prefix `/tm`.  
- **PySide6 + QtCharts** – תצוגת Desktop (חיפוש, פרטים, גרפים).  
- **JWT** – מנגנון הרשאות ואימות.  
- **CORS** פתוח לפיתוח מקומי.  

---

## 🗄️ מבנה טבלאות עיקרי
### Users
- `Id` (PK, Identity)  
- `Username`, `Email` (Unique)  
- `password_hash`, `role`, `is_active`, `CreatedAt`

### Events
- `Id` (PK, Identity)  
- `Title`, `Category`, `Date`, `Venue`, `City`, `Country`, `Url`  
- `Price DECIMAL(10,2)`, `CreatedAt`  
- אינדקסים: `IX_Events_Category`, `IX_Events_Date`  
- קשר זר: `Orders.EventId → Events.Id`

---

## 🚀 איך להריץ
1. התקנת סביבת פיתוח:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt

   בדיקות מהירות (Postman)

Login:
POST /auth/login → שמירת טוקן ל־{{token}}

Search DB:
GET /events/search?q=tel&category=Conference&page=1&limit=5

Get Event:
GET /events/1

Analytics:
GET /events/analytics/summary (Bearer)

Gateway:
GET /tm/events/search?q=tel

📌 מה עוד מתוכנן

Orders: יצירת הזמנות (POST /orders), הצגת הזמנות משתמש (GET /orders/my), וסטטיסטיקות לאדמין.

CRUD לאירועים (Admin): הוספה, עדכון, מחיקה עם הרשאת role.

סוכן AI (RAG): חיבור ל־Ollama Docker והוספת /ai/ask.

UI (PySide6): השלמת מסכים – חיפוש עם Toggle “כולל חיצוני”, פרטי אירוע, גרפים, והזמנות.
"""

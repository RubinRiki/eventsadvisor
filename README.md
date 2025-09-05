EventHub – מערכת לניהול אירועים
רעיון כללי

מערכת שולחנית (Desktop) לניהול וצריכת אירועי תרבות (סטנדאפ, מוזיקה וכו’).
המשתמשים יכולים לחפש אירועים, להירשם (קניית כרטיס), לקבל המלצות מ־AI Agent (Ollama), ולנהל אירועים בהתאם לתפקידם.

מודלים עיקריים

User – משתמש רגיל, סוכן (Agent) מפרסם אירועים, או מנהל (Admin).

Event – תיאור, קטגוריה, תאריך, מקום, קיבולת, תמונה, סטטוס.

Registration – חיבור משתמש ↔ אירוע (רשום / המתנה / ביטול).

Reaction (אופציונלי) – לייק / שמירה.

Agent Request – בקשות משתמשים להפוך לסוכנים.

תפקידים ופלואים

משתמש רגיל – חיפוש אירועים, הרשמה, לייקים/שמירה, בקשה להפוך לסוכן.

סוכן – יוצר/מפרסם/מעדכן את האירועים שלו.

מנהל – מאשר בקשות סוכן, מנהל אירועים/משתמשים, רואה דוחות.

מסכים עיקריים (PySide6)

דף בית / חיפוש – רשימת אירועים, סינון/חיפוש, גרפים/טבלאות (QtCharts).

פרטי אירוע – מידע מלא + הרשמה/ביטול.

פרופיל משתמש – הרשמות שלי, לייקים/שמורים, בקשה להפוך לסוכן.

לוח בקרה לסוכן – ניהול האירועים שלי + הוספת אירוע חדש.

ניהול אדמין – בקשות סוכן + דוחות.

רכיבי מערכת

Client – PySide6 Desktop App, QtCharts לגרפים.

Server – FastAPI, MVC + CQRS, שמירה בענן (somee).

Gateway – ניהול JWT, BFF למסכים, גישה לשירותים חיצוניים.

External – Ollama (AI Agent, RAG) לייעוץ והמלצות; Cloudinary לאחסון תמונות (אופציונלי).

DevOps – Docker להרצת Ollama, קוד מנוהל ב־GitHub.

עמידה בדרישות

חיפוש → פרטים → הרשמה (כרטיס) ✔️

גרף/טבלה עם QtCharts ✔️

התייעצות עם AI Agent (Ollama) ✔️

Gateway + MVC/CQRS ✔️

שמירה בענן (somee) ✔️

Docker + GitHub Repo ✔️

אופציה: Cloudinary ✔️


עדכונים מ 05/09/25:
נכון לעכשיו תיקיית models/ סגורה ומוכנה:

✅ user.py – עודכן עם role ו־agent_status.

✅ event.py – עודכן עם status, capacity, starts_at/ends_at וכו’.

✅ registration.py (במקום order.py) – עודכן עם status (CONFIRMED / WAITLIST / CANCELLED).

✅ analytics.py – חדש ומותאם ל־Dashboard/גרפים (Totals, ByMonth, ByCategory, ByEvent, Utilization%).

✅ db_models.py – ORM עם SQLAlchemy (UserDB, EventDB, RegistrationDB, AgentRequestDB).

⚠️ ai.py – קיים כמו שהיה, נשלים אותו כשנחבר את הסוכן/RAG.
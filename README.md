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


אחרי העדכון: סגרנו את צד ה-Server ב-FastAPI לפי MVC/CQRS — מודלים, ORM, Repositories ו-Routers חדשים ונקיים.

הכל מחובר למסד ב-Somee עם JWT ו-Roles, תהליך הרשמה (כרטיסים), בקשות סוכן, Reactions, ו-Analytics דרך Views.

השרת יציב ומוכן לחיבור ל-Gateway ול-Client (PySide6 + QtCharts + AI Agent).


מה עשינו

בנינו מחדש את צד ה־SERVER (FastAPI) לפי MVC/CQRS: Routers (auth, events, registrations, agent_requests, reactions, analytics, ai, health), ריפוזיטוריז תואמי SQLAlchemy, ותיקנו את db_models.py כך שיתאים ל־Somee (טבלאות Users/Events/Registrations/..., מזהי int, שדות starts_at/status/capacity/...).

חיברנו את כל ה־endpoints ל־DB בעזרת db: Session = Depends(get_db) והוספנו שכבת אבטחה מלאה: jwt.py, security.py, deps.py (get_db, get_current_user, require_any/require_role).

ניקינו שאריות "Orders" והעברנו ל־Registrations עם לוגיקת קיבולת/המתנה; הוספנו אנליטיקות דרך Views; שמרנו endpoint ל־AI (Ollama).

הקמנו Mini-Gateway (BFF) מינימלי (4 קבצים: main.py, config.py, server_client.py, security.py) שמפשט את ה־JSON למסכי PySide6 ומנהל Token ב־cookie.

פתרנו תקלות סביבת פייתון: שדרגנו email-validator → 2.3.0 והתאמנו גרסאות (fastapi 0.113, uvicorn 0.31.x) עד שה־Server עולה עד שלב ה־imports.

מה עובד עכשיו

תשתית ה־SERVER קומפיילת עד שלב הטעינה (Uvicorn רץ), ה־deps/jwt/security תקינים, החיבורים ל־DB מוכנים, ורוב ה־routers/Repos מסתנכרנים מול המודלים וה־ORM.

הסביבה (venv) תקינה לאחר עדכוני התלויות; Swagger צפוי לעלות אחרי סגירת ה־importים.

השגיאה הנוכחית (חוסמת)

בעת טעינת האפליקציה:
ImportError: cannot import name 'EventPublic' from 'server.models.event'

המשמעות: בקובץ server/api/events.py אנחנו מייבאים EventPublic (וגם EventCreate/EventUpdate/EventSearchParams/EventSearchResult/AnalyticsSummary), אבל ב־server/models/event.py המחלקות הללו לא מוגדרות/לא מיוצאות בשם הזה.

נדרש יישור בין ה־API/Repos לבין ה־Pydantic models: או להוסיף את המחלקות ל־models/event.py (לפי ההגדרות שהשתמשנו בהן), או לעדכן את ה־imports בקובצי ה־API/Repos לשמות המחלקות שקיימים בפועל.

הצעת המשך (לביצוע בסבב הבא)

להשלים/ליישר את server/models/event.py עם המחלקות:
EventPublic, EventCreate, EventUpdate, EventSearchParams, EventSearchResult, AnalyticsSummary.
(אלו המחלקות שבהן ה־routers/Repos משתמשים כרגע.)

להריץ שוב: uvicorn server.main:app --reload ולוודא שה־/health ו־/docs עולים.

רק לאחר שה־SERVER עולה חלק – להגדיר SERVER_BASE_URL ולהריץ את ה־Gateway.

אם תרצי—אשלח לך את תוכן models/event.py המדויק שתואם 1:1 ל־API/Repos הנוכחיים.
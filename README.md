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

בגדול תקית הSERVER אמורה להיות סגורה- הכוונה שהיא ממומשת במלואה ולא אמור להיות שינויים. 

סיכום מצב פרויקט EventHub
מה יש ועובד

שרת FastAPI עולה ורץ עם כל ה־routers.

מודול Auth

רישום משתמשים (/auth/register) עובד.

התחברות (/auth/login) נבדק ועובד, מחזיר טוקן JWT תקין.

Ollama (AI)

Docker רץ, מודל llama3.1 מותקן.

חיבור דרך /ai/ask מחזיר תשובה אמיתית מהמודל.

Health

Endpoint בסיסי /health מחזיר סטטוס תקין.

מבנה קוד

כל המודלים וה־repositories מוגדרים.

כל ה־routers קיימים ומחוברים ב־main.py.

קבצי __init__.py הוספו כדי לאפשר ייבוא תקין.

מה חסר / לא נבדק

בדיקות ראוטרים נוספים:

Events (/events) – יצירה, חיפוש, עדכון סטטוס.

Registrations (/registrations) – הרשמה, ביטול, רשימת רישומים.

Reactions (/reactions) – לייק/שמירה.

Agent Requests (/agent-requests) – בקשות להפוך לסוכן, אישור/דחייה.

Analytics (/analytics/summary) – החזרת סיכומי נתונים.

Seed Data – עדיין אין נתוני דמו (משתמשים, אירועים, רישומים).

Client (PySide6) – לא חובר עדיין ל־API (מסכים, גרפים עם QtCharts).

הרשאות – לא נבדק שכל החוקים (USER/AGENT/ADMIN) פועלים בפועל.

שגיאות DB – צריך לבדוק חיבורים/טיים־אאוטים מול somee בפועל.

RAG – כרגע ה־AI עונה כללי בלבד; אין הקשר מה־DB של האירועים.

בדיקות End-to-End – צריך לעבור ב־Postman/GUI על כל הפלואו:
רישום → התחברות → יצירת אירוע → הרשמה → לייק/שמירה → Analytics.










מה כבר עשינו יום ראשון

צד שרת (server)

בנינו מודלים (UserDB, EventDB, RegistrationDB, ReactionsDB, AgentRequestDB).

יצרנו Pydantic Models (Public / Create) לכל ישות.

כתבנו Repositories לכל ישות (users, events, registrations, reactions, agent_requests).

בנינו Routers ב־FastAPI (auth, events, registrations, reactions, agent-requests).

חיברנו JWT + אבטחה (get_current_user, require_role וכו').

הוספנו seed data (משתמשים, אירועים, הרשמות, לייקים, agent requests).

צד לקוח (client, PySide6)

יש לנו מבנה מסודר:

client/
  app.py
  app_shell.py
  views/
  ui/
  core/
  gateway/


כתבנו app.py שמרים את ה־QApplication ואת ה־AppShell.

כתבנו AppShell עם Sidebar, StackedWidget ו־views.

הוספנו LoginView שמבצע קריאה ל־auth/login בשרת ושומר את ה־JWT.

הכנו auth_service ב־gateway שמתקשר לשרת.

דיבאג

פתרנו בעיות של נתונים חסרים בטבלאות.

תיקנו imports שקשורים ל־client.gateway.auth_service.

כרגע השגיאה היא ש־views מנסים לייבא ui כאילו היא חבילה ברמה העליונה, אבל בעצם היא תחת client/ui.

❌ מה עדיין בעייתי

Imports לא נכונים:
בקבצי views (כמו details_view.py, search_view.py) מופיע:

from ui.components.cards import Card


אבל זה צריך להיות:

from client.ui.components.cards import Card


או בגרסה יחסית:

from ..ui.components.cards import Card


בדיקת UI בלייב:
עוד לא ראינו את מסך ה־Login עובד באמת, כי הקוד נתקע על ה־imports.

⏭ מה נשאר לנו לעשות

לתקן imports בכל ה־views שקשורים ל־ui → לשים client.ui... או ..ui....

להריץ שוב את האפליקציה ולבדוק שה־LoginView נפתח, ואפשר להכניס מייל+סיסמה.

לבדוק שה־login שולח בקשה לשרת ומחזיר JWT.

אחרי שזה עובד – להמשיך ל־SearchView ולחבר אותו ל־API של events/search.

משם – לבנות לאט לאט את שאר המסכים (Details, Charts, Consult) לפי ההוראות של ה־MVP.

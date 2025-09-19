# server/api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.core.deps import get_db, get_current_user
from server.core.security import hash_password
from server.models.user import UserPublic, UserUpdate
from server.repositories.users_repo import repo_users

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserPublic)
def get_me(current: UserPublic = Depends(get_current_user)):
    # current כבר מכיל id/username/email/role (מגיע מ-JWT)
    return current

@router.patch("/me", response_model=UserPublic)
def update_me(
    body: UserUpdate,
    current: UserPublic = Depends(get_current_user),
):
    # מאחר וה-UsersRepository הנוכחי לא כולל update, נעדכן ברמת DB "ידנית".
    # אפשר להרחיב את הרפוזיטורי אם תרצי. כאן נשתמש בחיבור ישיר לפי הדוגמה הקיימת.
    from server.repositories.users_repo import _conn  # reuse same DSN
    fields = []
    values = []
    if body.username is not None:
        fields.append("Username = ?")
        values.append(body.username.strip())
    if body.role is not None:
        fields.append("role = ?")
        values.append(body.role.upper())
    if not fields:
        return current
    values.append(int(current.id))
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE Users SET {', '.join(fields)} WHERE Id = ?",
            tuple(values),
        )
        # קראי חזרה את המשתמש
        cur.execute("SELECT Id, Username, Email, password_hash, role, is_active FROM Users WHERE Id = ?", (int(current.id),))
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="user not found")
    # המרה חזרה ל-UserPublic לפי הצורה הקיימת
    return UserPublic(
        id=int(row[0]),
        username=row[1],
        email=row[2],
        role=(row[4] or "USER").upper(),
        agent_status="NONE",
        is_active=bool(row[5]),
    )

class PasswordChangeBody(UserUpdate):
    # משתמשים ב-UserUpdate כ-base כדי להימנע מסכמות מיותרות; נשתמש רק בשדה 'password'
    password: str | None = None

@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: PasswordChangeBody,
    current: UserPublic = Depends(get_current_user),
):
    if not body.password or len(body.password) < 6:
        raise HTTPException(status_code=400, detail="password too short")
    pwd_hash = hash_password(body.password)
    from server.repositories.users_repo import _conn
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE Users SET password_hash = ? WHERE Id = ?", (pwd_hash, int(current.id)))
    return

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash

db = next(get_db())

users = db.query(User).all()
for u in users:
    u.hashed_password = get_password_hash("test123")
    db.commit()

print("所有用户密码已重置为 test123")
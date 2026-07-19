from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password

db = next(get_db())
users = db.query(User).all()
for u in users:
    print(f'User: {u.username}, Email: {u.email}, ID: {u.id}')
    print(f'  Password hash: {u.hashed_password[:50]}...')
    print(f'  Verify test123: {verify_password("test123", u.hashed_password)}')
from fastapi import APIRouter, HTTPException, Query
from app.models.user_models import RegisterRequest, LoginRequest
from app.services.storage import save_user, load_user, update_user_verified
from app.services.utils import hash_password, check_password, generate_token, verify_token
from app.services.email_utils import send_verification_email

router = APIRouter()

@router.post("/register")
def register_user(req: RegisterRequest):
    if load_user(req.email):
        raise HTTPException(400, "User already exists.")
    hashed_pw = hash_password(req.password)
    token = generate_token(req.email)
    user = {"email": req.email, "password": hashed_pw, "verified": False, "token": token}
    save_user(user)
    send_verification_email(req.email, token)
    return {"message": "Check your email to verify your account."}

@router.get("/verify")
def verify_user(token: str = Query(...)):
    email = verify_token(token)
    if not email:
        raise HTTPException(400, "Invalid or expired token.")
    update_user_verified(email)
    return {"message": "Email verified."}

@router.post("/login")
def login_user(req: LoginRequest):
    user = load_user(req.email)
    if not user or not check_password(req.password, user["password"]):
        raise HTTPException(401, "Invalid credentials.")
    if not user["verified"]:
        raise HTTPException(403, "Email not verified.")
    return {"message": "Login successful."}
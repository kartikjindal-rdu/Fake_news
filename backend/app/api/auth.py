from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(req: LoginRequest):
    return {
        "token": "veritas_jwt_auth_token_mock_payload_2026",
        "user": {
            "name": "Research Investigator",
            "email": req.email,
            "role": "Lead Intelligence Analyst",
            "tier": "Enterprise Tier"
        }
    }

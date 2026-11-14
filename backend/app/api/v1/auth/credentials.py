from fastapi import APIRouter, Depends, Response, status

from app.api.deps import SettingsDep, rate_limit
from app.api.v1.auth.deps import AuthServiceDep, ClientDep, UserAgentDep
from app.api.v1.auth.schemas import LoginRequest, RegisterRequest, TokenPair
from app.api.v1.auth.tokens import token_pair

router = APIRouter()


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    summary="Create an account and sign in",
    dependencies=[Depends(rate_limit("register"))],
    responses={409: {"description": "Email is already registered"}},
)
async def register(
    payload: RegisterRequest,
    response: Response,
    svc: AuthServiceDep,
    client: ClientDep,
    user_agent: UserAgentDep,
    settings: SettingsDep,
) -> TokenPair:
    tokens = await svc.register(
        email=payload.email,
        password=payload.password,
        username=payload.username,
        client=client,
        user_agent=user_agent,
    )
    return token_pair(response, tokens, client, settings)


@router.post(
    path="/login",
    summary="Sign in with email and password",
    dependencies=[Depends(rate_limit("login"))],
    responses={401: {"description": "Wrong email or password"}},
)
async def login(
    payload: LoginRequest,
    response: Response,
    svc: AuthServiceDep,
    client: ClientDep,
    user_agent: UserAgentDep,
    settings: SettingsDep,
) -> TokenPair:
    tokens = await svc.login(
        email=payload.email, password=payload.password, client=client, user_agent=user_agent
    )
    return token_pair(response, tokens, client, settings)

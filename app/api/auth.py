from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import WeChatLoginRequest, TokenResponse, UserResponse
from app.utils.auth import get_wechat_openid, create_access_token
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def wechat_login(
    login_data: WeChatLoginRequest,
    db: Session = Depends(get_db)
):
    """WeChat mini-program login"""
    # Get openid from WeChat
    openid = await get_wechat_openid(login_data.code)
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid WeChat code"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.openid == openid).first()
    
    if not user:
        # Create new user
        user = User(
            openid=openid,
            nickname=login_data.nickname,
            avatar=login_data.avatar
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user info if provided
        if login_data.nickname:
            user.nickname = login_data.nickname
        if login_data.avatar:
            user.avatar = login_data.avatar
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

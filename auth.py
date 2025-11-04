"""
Entra ID (Azure AD) 認証とトークン検証
"""

import os
import logging
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWKClient
import azure.functions as func

logger = logging.getLogger(__name__)

# Entra ID設定
TENANT_ID = os.getenv("ENTRA_TENANT_ID")
CLIENT_ID = os.getenv("ENTRA_CLIENT_ID")  # API のClient ID
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

# 認証を有効にするかどうか
AUTH_ENABLED = os.getenv("ENABLE_ENTRA_AUTH", "false").lower() == "true"


class AuthenticationError(Exception):
    """認証エラー"""
    pass


def get_token_from_request(req: func.HttpRequest) -> Optional[str]:
    """HTTPリクエストからBearerトークンを取得"""
    auth_header = req.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    return auth_header[7:]  # "Bearer " を削除


def verify_token(token: str) -> Dict[str, Any]:
    """
    Entra IDトークンを検証
    
    Args:
        token: JWTトークン
        
    Returns:
        デコードされたトークンのペイロード
        
    Raises:
        AuthenticationError: トークンが無効な場合
    """
    if not TENANT_ID or not CLIENT_ID:
        raise AuthenticationError("Entra ID configuration is missing (TENANT_ID or CLIENT_ID)")
    
    try:
        # JWKSクライアントを使用して公開鍵を取得
        jwks_client = PyJWKClient(JWKS_URI)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # トークンを検証・デコード
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLIENT_ID,  # APIのClient ID
            issuer=ISSUER,
        )
        
        logger.info(f"Token verified for user: {payload.get('preferred_username', 'unknown')}")
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidAudienceError:
        raise AuthenticationError("Invalid token audience")
    except jwt.InvalidIssuerError:
        raise AuthenticationError("Invalid token issuer")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise AuthenticationError(f"Token verification failed: {str(e)}")


def require_auth(func_handler):
    """
    Azure Function用の認証デコレータ
    
    使用例:
        @require_auth
        def my_function(req: func.HttpRequest) -> func.HttpResponse:
            # req.user_info に認証情報が含まれる
            user_id = req.user_info.get('oid')
            ...
    """
    def wrapper(req: func.HttpRequest) -> func.HttpResponse:
        # 認証が無効な場合はそのまま実行
        if not AUTH_ENABLED:
            logger.debug("Authentication is disabled")
            req.user_info = None  # type: ignore
            return func_handler(req)
        
        # トークンを取得
        token = get_token_from_request(req)
        
        if not token:
            logger.warning("No authentication token provided")
            return func.HttpResponse(
                body='{"error": "Authentication required. Please provide a valid Bearer token."}',
                status_code=401,
                mimetype="application/json",
                headers={
                    "WWW-Authenticate": "Bearer"
                }
            )
        
        # トークンを検証
        try:
            user_info = verify_token(token)
            req.user_info = user_info  # type: ignore
            logger.info(f"Authenticated request from user: {user_info.get('preferred_username')}")
            
        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {str(e)}")
            return func.HttpResponse(
                body=f'{{"error": "Authentication failed", "details": "{str(e)}"}}',
                status_code=401,
                mimetype="application/json",
                headers={
                    "WWW-Authenticate": "Bearer"
                }
            )
        
        # 認証成功、元の関数を実行
        return func_handler(req)
    
    return wrapper


def get_user_id(req: func.HttpRequest) -> Optional[str]:
    """
    リクエストからユーザーIDを取得
    
    Args:
        req: HttpRequest with user_info attribute
        
    Returns:
        ユーザーID（object ID）またはNone
    """
    if hasattr(req, 'user_info') and req.user_info:
        return req.user_info.get('oid')  # object ID
    return None


def get_user_name(req: func.HttpRequest) -> Optional[str]:
    """
    リクエストからユーザー名を取得
    
    Args:
        req: HttpRequest with user_info attribute
        
    Returns:
        ユーザー名またはNone
    """
    if hasattr(req, 'user_info') and req.user_info:
        return req.user_info.get('preferred_username') or req.user_info.get('name')
    return None

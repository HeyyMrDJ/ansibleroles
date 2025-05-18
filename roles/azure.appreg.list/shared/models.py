from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PasswordCredential(BaseModel):
    endDateTime: datetime
    keyId: str

class AppRegistration(BaseModel):
    appId: str
    displayName: str
    tags: List[str] = []
    passwordCredentials: Optional[List[PasswordCredential]] = None

class ExpiredPasswordCredential(BaseModel):
    endDateTime: datetime
    keyId: str

class ExpiredApp(BaseModel):
    appId: str
    displayName: str
    expiredCredentials: List[ExpiredPasswordCredential]

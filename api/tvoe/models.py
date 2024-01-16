from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BaseRequestModel(BaseModel):
    text: str
    status_code: int
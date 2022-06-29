from pydantic import BaseModel


# Result's default max_length
MIN_LENGTH = 1

# generate function request form
class APIRequest(BaseModel):
    code: str
    max_length: int = MIN_LENGTH

# generate function response form
class APIResponse(BaseModel):
    text: str

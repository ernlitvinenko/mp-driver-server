from fastapi.responses import JSONResponse


class MPDriverException(Exception):
    def __init__(self, status: int, name: str = None, mnemonic: str = None, detail: str = None, personalized_status: int = None):
        self.status = status
        self.name = name
        self.mnemonic = mnemonic
        self.personalized_status = personalized_status if personalized_status else self.status
        self.detail = detail

    def response(self):
        content = {
            "status": self.personalized_status,
            "error": self.name,
            "detail": self.detail,
            "langs": {
                "ru": self.mnemonic
            }
        }
        return JSONResponse(content, status_code=self.status)

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging


logger = logging.getLogger("uvicorn.error")


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as ex:
            return JSONResponse(
                status_code=ex.status_code,
                content={"detail": ex.detail}
            )
        except Exception as ex:
            logger.error(f"Unhandled error: {ex}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )

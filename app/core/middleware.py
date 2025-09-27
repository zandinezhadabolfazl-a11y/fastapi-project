
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # پردازش درخواست
        response = await call_next(request)

        # زمان پردازش
        process_time = time.time() - start_time
        print(f"➡️ {request.method} {request.url} - ⏱ {process_time:.4f} sec")

        # می‌تونی هدر هم به همه ریسپانس‌ها اضافه کنی
        response.headers["X-Process-Time"] = str(process_time)

        return response

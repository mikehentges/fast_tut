import httpx

from app.config import config


class APIResponseError(Exception):
    pass


async def send_simple_email(to: str, subject: str, text: str) -> None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"FastAPI User <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": text,
                },
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            raise APIResponseError(e.response.json()) from e

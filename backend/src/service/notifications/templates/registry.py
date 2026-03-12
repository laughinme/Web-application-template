from .email_templates import EmailTemplate, render_email_template
from .telegram_templates import render_telegram_template


class TemplateRegistry:
    @staticmethod
    def email(event_type: str, payload: dict) -> EmailTemplate | None:
        return render_email_template(event_type, payload)

    @staticmethod
    def telegram(event_type: str, payload: dict) -> str | None:
        return render_telegram_template(event_type, payload)

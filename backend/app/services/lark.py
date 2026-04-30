import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_lark_action_token
from app.models.customer import Customer
from app.models.ticket import Ticket
from app.services.settings import SettingsService


class LarkService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def push_ticket(self, customer: Customer, ticket: Ticket) -> dict:
        settings_map = await SettingsService(self.session).get_settings_map()
        webhook_url = settings_map.get("lark_webhook_url", "")
        if not webhook_url:
            return {"message": "Lark webhook URL is not configured"}

        backend_base_url = settings_map.get("backend_public_base_url", "").rstrip("/")
        frontend_base_url = settings_map.get("frontend_public_base_url", "").rstrip("/")
        if not backend_base_url or not frontend_base_url:
            return {"message": "Frontend/backend public base URLs are not configured"}

        accept_token = create_lark_action_token(ticket.id, "accept")
        done_token = create_lark_action_token(ticket.id, "done")
        accept_url = f"{backend_base_url}/api/webhooks/lark/action?token={accept_token}"
        done_url = f"{backend_base_url}/api/webhooks/lark/action?token={done_token}"
        detail_url = f"{frontend_base_url}/tickets?ticket={ticket.id}"

        request_title = self._default_title(ticket.type.value)
        request_category = self._format_ticket_type(ticket.type.value)
        platform_label = self._format_platform(ticket.platform.value)
        note = ticket.note or "Không có ghi chú"

        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True, "enable_forward": True},
                "header": {
                    "template": self._status_template(ticket.status.value),
                    "title": {"tag": "plain_text", "content": self._status_title(ticket.status.value)},
                },
                "elements": [
                    {"tag": "markdown", "content": f"**{request_title}**"},
                    {
                        "tag": "div",
                        "fields": [
                            {"is_short": False, "text": {"tag": "lark_md", "content": f"**Khách hàng:** {customer.full_name}"}},
                            {"is_short": True, "text": {"tag": "lark_md", "content": f"**Hạng mục:** {request_category}"}},
                            {"is_short": True, "text": {"tag": "lark_md", "content": f"**Nền tảng:** {platform_label}"}},
                            {"is_short": False, "text": {"tag": "lark_md", "content": f"**Ghi chú:** {note}"}},
                        ],
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "Xem chi tiết"},
                                "type": "default",
                                "url": detail_url,
                            },
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "Đã tiếp nhận"},
                                "type": "default",
                                "url": accept_url,
                            },
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "Hoàn thành"},
                                "type": "primary",
                                "url": done_url,
                            },
                        ],
                    },
                    {"tag": "note", "elements": [{"tag": "plain_text", "content": f"CRM • Ticket #{ticket.id}"}]},
                ],
            },
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def _default_title(ticket_type: str) -> str:
        if ticket_type == "open_account":
            return "Yêu cầu mở tài khoản"
        return "Hỗ trợ hệ thống"

    @staticmethod
    def _status_title(status: str) -> str:
        return {
            "pending": "Có 1 yêu cầu mới",
            "processing": "Yêu cầu đang được tiếp nhận",
            "done": "Yêu cầu đã hoàn thành",
            "rejected": "Yêu cầu đã bị từ chối",
        }.get(status, "Cập nhật ticket")

    @staticmethod
    def _status_template(status: str) -> str:
        return {
            "pending": "orange",
            "processing": "blue",
            "done": "green",
            "rejected": "red",
        }.get(status, "blue")

    @staticmethod
    def _format_ticket_type(ticket_type: str) -> str:
        return {
            "open_account": "Mở tài khoản",
            "support": "Hỗ trợ",
        }.get(ticket_type, ticket_type)

    @staticmethod
    def _format_platform(platform: str) -> str:
        return {
            "facebook": "Facebook",
            "tiktok": "TikTok",
            "google": "Google",
        }.get(platform, platform)

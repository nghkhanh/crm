from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.ad_account import AdAccount, AdAccountStatus, Platform
from app.models.customer import Customer, CustomerStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.referral import Referral
from app.models.ticket import Ticket, TicketStatus, TicketType
from app.models.transaction import Transaction, TransactionSource, TransactionStatus, TransactionType
from app.models.user import User


async def seed_demo_data() -> None:
    async with AsyncSessionLocal() as session:
        existing_customer = await session.scalar(select(Customer.id).limit(1))
        if existing_customer:
            return

        admin = await session.scalar(select(User).where(User.email == settings.default_admin_email))
        admin_id = admin.id if admin else None

        customers = [
            Customer(
                full_name="Nguyen Van An",
                email="an@example.com",
                phone="0901234567",
                telegram_id="@nguyenvanan",
                referral_code="AN001",
                referred_by=admin_id,
                wallet_balance=Decimal("1250.00"),
                status=CustomerStatus.active,
                note="Khach hang uu tien, chay Facebook Ads cho ecommerce.",
            ),
            Customer(
                full_name="Tran Thi Binh",
                email="binh@example.com",
                phone="0912345678",
                telegram_id="@tranthibinh",
                referral_code="BINH001",
                referred_by=admin_id,
                wallet_balance=Decimal("540.00"),
                status=CustomerStatus.active,
                note="Khach hang can ho tro nhieu ve topup.",
            ),
            Customer(
                full_name="Le Minh Cuong",
                email="cuong@example.com",
                phone="0987654321",
                telegram_id="@leminhcuong",
                referral_code="CUONG001",
                referred_by=admin_id,
                wallet_balance=Decimal("0.00"),
                status=CustomerStatus.inactive,
                note="Tam dung do khong phat sinh chi tieu.",
            ),
        ]
        session.add_all(customers)
        await session.flush()

        ad_accounts = [
            AdAccount(
                customer_id=customers[0].id,
                platform=Platform.facebook,
                account_id="1000001",
                account_name="AN - Fashion Store",
                status=AdAccountStatus.active,
                balance=Decimal("800.00"),
                spend_today=Decimal("73.40"),
                spend_7d=Decimal("412.25"),
                spend_28d=Decimal("1620.10"),
                spend_90d=Decimal("4320.55"),
                business_license_name="AN Fashion Co",
                request_id="REQ-1001",
                team_id="TEAM-A",
            ),
            AdAccount(
                customer_id=customers[1].id,
                platform=Platform.facebook,
                account_id="1000002",
                account_name="BINH - Education Leads",
                status=AdAccountStatus.disabled,
                balance=Decimal("120.00"),
                spend_today=Decimal("0.00"),
                spend_7d=Decimal("85.00"),
                spend_28d=Decimal("320.50"),
                spend_90d=Decimal("980.40"),
                business_license_name="Binh Education",
                request_id="REQ-1002",
                team_id="TEAM-B",
            ),
        ]
        session.add_all(ad_accounts)

        transactions = [
            Transaction(
                customer_id=customers[0].id,
                type=TransactionType.topup_bank,
                source=TransactionSource.manual,
                status=TransactionStatus.posted,
                amount=Decimal("1000.00"),
                balance_before=Decimal("285.00"),
                balance_after=Decimal("1285.00"),
                reference="VCB-22001",
                note="Nap tien qua ngan hang",
                created_by=admin_id,
            ),
            Transaction(
                customer_id=customers[0].id,
                type=TransactionType.fee,
                source=TransactionSource.manual,
                status=TransactionStatus.posted,
                amount=Decimal("35.00"),
                balance_before=Decimal("1285.00"),
                balance_after=Decimal("1250.00"),
                reference="FEE-22001",
                note="Phi dich vu thang",
                created_by=admin_id,
            ),
            Transaction(
                customer_id=customers[1].id,
                type=TransactionType.topup_usdt,
                source=TransactionSource.manual,
                status=TransactionStatus.posted,
                amount=Decimal("540.00"),
                balance_before=Decimal("0.00"),
                balance_after=Decimal("540.00"),
                reference="TRX-22001",
                note="Nap USDT TRC20",
                created_by=admin_id,
            ),
        ]
        session.add_all(transactions)

        invoices = [
            Invoice(
                customer_id=customers[0].id,
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_topup=Decimal("1000.00"),
                total_fee=Decimal("35.00"),
                total_commission=Decimal("0.00"),
                file_url=None,
                status=InvoiceStatus.sent,
            ),
            Invoice(
                customer_id=customers[1].id,
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_topup=Decimal("540.00"),
                total_fee=Decimal("12.00"),
                total_commission=Decimal("0.00"),
                file_url=None,
                status=InvoiceStatus.draft,
            ),
        ]
        session.add_all(invoices)

        tickets = [
            Ticket(
                customer_id=customers[0].id,
                type=TicketType.support,
                platform=Platform.facebook,
                status=TicketStatus.processing,
                form_data={"issue": "Tai khoan bi giam reach"},
                note="Dang nhan phan hoi tu team account",
            ),
            Ticket(
                customer_id=customers[1].id,
                type=TicketType.open_account,
                platform=Platform.facebook,
                status=TicketStatus.pending,
                form_data={"business_name": "Binh Education"},
                note="Cho day du giay phep kinh doanh",
            ),
        ]
        session.add_all(tickets)

        session.add(
            Referral(
                referrer_id=customers[0].id,
                referee_id=customers[1].id,
                commission_rate=Decimal("5.00"),
                total_earned=Decimal("27.00"),
            )
        )

        await session.commit()

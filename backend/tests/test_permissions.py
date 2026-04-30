from app.models.user import Permission, User, UserRole


def test_cs_permissions_are_limited():
    user = User(email="cs@example.com", password_hash="x", full_name="CS", role=UserRole.cs)

    assert user.has_permission(Permission.customer_read)
    assert user.has_permission(Permission.ticket_push_lark)
    assert not user.has_permission(Permission.transaction_write)
    assert not user.has_permission(Permission.settings_write)


def test_accountant_permissions_are_limited():
    user = User(email="acc@example.com", password_hash="x", full_name="Accountant", role=UserRole.accountant)

    assert user.has_permission(Permission.invoice_write)
    assert user.has_permission(Permission.transaction_read)
    assert not user.has_permission(Permission.ticket_write)
    assert not user.has_permission(Permission.ad_account_sync)

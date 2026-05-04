import pytest

from app.schemas.customer import CustomerCreate


def test_customer_create_requires_email():
    with pytest.raises(ValueError):
        CustomerCreate(full_name="Customer A", email="")


def test_customer_create_requires_non_empty_name():
    with pytest.raises(ValueError):
        CustomerCreate(full_name="   ", email="customer@example.com")

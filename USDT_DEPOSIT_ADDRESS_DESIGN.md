# USDT Deposit Address Design

Muc tieu: phan biet chinh xac khach hang nao nap USDT vao CRM bang cach cap `1 dia chi nap rieng / customer`, thay vi dung chung mot vi va doan theo `memo` hoac `referral_code`.

## Nguyen tac

- Tren Tron / TRC20, khong co "sub-wallet tu vi chinh" theo nghia native.
- Giai phap kha thi la quan ly `deposit address` rieng cho tung customer.
- CRM se luu mapping `customer -> deposit address`.
- Poller TronGrid se doc giao dich cua tung dia chi nap dang active.
- Khi co giao dich vao dia chi do:
  - ghi nhan transaction `topup_usdt`
  - cong `wallet_balance`
  - luu audit + idempotency theo `transaction_id`

## Phase 1 da scaffold

- Model `customer_usdt_addresses`
- API gan dia chi USDT cho customer
- Poll TronGrid match theo `to_address`
- Dung `WebhookEvent` de chong credit lap lai

## Luong nghiep vu

1. Tao customer
2. Cap 1 dia chi nap USDT rieng cho customer
3. Khach chuyen USDT vao dia chi do
4. Job TronGrid poll dinh ky
5. Neu `transaction_id` chua xu ly:
   - tao `transactions`
   - cong `wallet_balance`
   - cap nhat `last_seen_at` tren dia chi nap

## Nhung gi chua lam trong Phase 1

- Tu dong sinh vi moi cho customer
- Sweep tien ve vi tong cua agency
- Quan ly private key / custody / gas TRX
- UI cap dia chi nap tren customer detail
- Reconciliation dashboard cho nap USDT

## Khuyen nghi triem khai that

- Neu agency tu quan ly vi: can them key management va sweep worker.
- Neu muon an toan hon: dung provider custody/virtual account de cap dia chi nap va webhook on-chain.
- Trong moi truong hien tai, CRM nen la he thong mapping + doi soat + credit wallet, khong nen tu giu private key neu chua co quy trinh van hanh an toan.

# Enterprise Product Roadmap

This roadmap turns the current CRM into a production-standard internal business system.

## Current status

- Core backend and frontend are running
- Auth, roles, dashboard, customers, ad accounts, transactions, invoices, tickets, referrals, settings, audit logs are present
- Facebook, Lark, SePay, and TronGrid integrations exist in code
- Docker healthchecks, readiness checks, and backend test suite are in place

The platform is suitable for controlled internal rollout, but not yet fully hardened for enterprise production.

## Phase 1: Production hardening

Target: make the platform safe for real internal business use.

### Security

- Replace coarse role checks with permission-based access control
- Add password reset flow
- Add password policy and login lockout
- Add rate limiting for auth and webhook endpoints
- Expand audit logs for login, logout, token refresh, settings, finance, and ticket actions
- Move secret handling to production-safe environment/secret management

### Finance correctness

- Add idempotency for SePay and USDT webhook/poll processing
- Add transaction reconciliation rules
- Prevent duplicate external references
- Add finance correction workflow instead of direct destructive edits
- Lock invoice periods after close

### Integrations

- Validate Facebook sync against real Business Manager data
- Validate SePay webhook payloads with real sandbox or production sample
- Validate TronGrid polling against real wallet transactions
- Validate Lark interactive flow end-to-end with public URLs
- Add retries and structured failure logging for all external calls

### Operations

- Add error tracking and structured application logging
- Add backup and restore procedure for PostgreSQL
- Add staging environment and release checklist
- Add deployment rollback checklist

### QA

- Add integration tests for auth refresh flow, transactions, invoices, and webhooks
- Add frontend end-to-end tests for critical user journeys
- Add smoke test checklist for each release

## Phase 2: Workflow completion

Target: complete the business flows so staff can use the system without side channels.

### Customers

- Full edit flow in UI
- Search, filter, and pagination
- Safer deactivation flow instead of delete-first behavior
- Customer activity timeline

### Ad accounts

- Filter by customer, status, and platform in UI
- Manual overrides with audit trail
- Better sync error visibility

### Transactions and invoices

- Search and date filters in UI
- Export invoice to PDF
- Add downloadable invoice file management
- Add commission ledger view

### Tickets

- Assignment to staff member
- SLA fields and aging indicators
- Detailed ticket thread/history
- Better Lark status synchronization

### Referral

- Commission history ledger
- Recalculation audit trail
- Better referral search/filter

## Phase 3: Enterprise visibility

Target: add management reporting and operational oversight.

### Dashboard and analytics

- Account block rate by quarter
- 90-day account health trend
- Spend trend by platform and team
- Ticket turnaround metrics
- Customer wallet utilization metrics

### Audit and admin

- Audit log filters by user, entity, action, date
- Export audit reports
- Integration status dashboard

### Notifications

- In-app alerts for failed sync jobs
- Finance mismatch alerts
- Expiring token alerts

## Phase 4: Scale and platform maturity

Target: prepare for larger teams or multiple business units.

### Architecture and scale

- Background job persistence and retry queue
- Better scheduler/job observability
- Load testing and DB tuning
- Caching strategy for heavy dashboards

### Organization support

- Team-based scoping
- Optional multi-tenant support
- More granular permissions by department

### Product polish

- Bulk actions
- Import/export tools
- Mobile usability pass
- UX refinement for large data sets

## Recommended implementation order

1. Phase 1 security and finance hardening
2. Phase 1 integration validation
3. Phase 1 backup, monitoring, release process
4. Phase 2 CRUD and workflow completion
5. Phase 3 analytics and admin visibility
6. Phase 4 scale and organizational expansion

## Definition of "enterprise-ready"

Do not call the product enterprise-ready until all of the following are true:

- Real integrations are validated end-to-end
- Finance flows are idempotent and auditable
- Access control is permission-based
- Monitoring, backup, and restore are documented and tested
- Critical backend and frontend flows have automated tests
- Release and rollback process is repeatable

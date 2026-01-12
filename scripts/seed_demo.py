import argparse
import json
import os
import sqlite3
import time

DB_PATH = os.environ.get("DATA_DB", "data.db")

DEMO_ORDER = (
    "demo_order_1",
    49900,
    "INR",
    "demo_receipt_1",
    "starter",
    "paid",
)
DEMO_PAYMENT = ("demo_pay_1", "demo_order_1")
DEMO_WEBHOOK = ("demo_webhook_1", "payment.captured")


def ensure_db():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"DB not found: {DB_PATH}. Run migrations first (alembic upgrade head).")


def seed(conn):
    now = time.time()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO orders (id, amount, currency, receipt, product, status, created_at, paid_at) VALUES (?,?,?,?,?,?,?,?)",
        (*DEMO_ORDER, now, now),
    )
    c.execute(
        "INSERT OR REPLACE INTO payments (id, order_id, payload, received_at) VALUES (?,?,?,?)",
        (*DEMO_PAYMENT, json.dumps({"note": "demo payment"}), now),
    )
    c.execute(
        "INSERT OR REPLACE INTO webhooks (id, event, payload, received_at) VALUES (?,?,?,?)",
        (*DEMO_WEBHOOK, json.dumps({"note": "demo webhook"}), now),
    )
    conn.commit()
    print("Seeded demo order/payment/webhook.")


def clear(conn):
    c = conn.cursor()
    for table in ("orders", "payments", "webhooks"):
        c.execute(f"DELETE FROM {table}")
    conn.commit()
    print("Cleared demo data (all rows removed from orders/payments/webhooks).")


def status(conn):
    c = conn.cursor()
    counts = {}
    for table in ("orders", "payments", "webhooks"):
        c.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = c.fetchone()[0]
    print(json.dumps({"db": DB_PATH, "counts": counts}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Seed or clear demo data for the Flask app")
    parser.add_argument("action", choices=["seed", "clear", "status"], help="What to do")
    args = parser.parse_args()

    ensure_db()
    conn = sqlite3.connect(DB_PATH)

    if args.action == "seed":
        seed(conn)
    elif args.action == "clear":
        clear(conn)
    elif args.action == "status":
        status(conn)


if __name__ == "__main__":
    main()

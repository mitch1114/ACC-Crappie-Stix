#!/usr/bin/env python3
"""Convert WooCommerce orders into a Matrixify (Excelify) order import CSV.

Shopify has no built-in order import, so historical orders go in via the
Matrixify app (matrixify.app). Install it on the Shopify store, then import
the file this script produces.

Reads:  migration/data/orders.json
Writes: migration/output/matrixify_orders.csv

Order numbers keep their WooCommerce number with a "W" prefix (e.g. #W12345)
so they can never collide with new Shopify order numbers. Imported orders are
tagged "woocommerce-import" and marked so no notification emails are sent.
"""

import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "output"

FINANCIAL_STATUS = {
    "pending": "pending",
    "processing": "paid",
    "on-hold": "pending",
    "completed": "paid",
    "cancelled": "voided",
    "refunded": "refunded",
    "failed": "voided",
}

FULFILLMENT_STATUS = {
    "completed": "fulfilled",
    "refunded": "fulfilled",
}

COLUMNS = [
    "Name", "Command", "Send Receipt", "Processed At", "Cancelled At",
    "Currency", "Email", "Phone", "Note", "Tags", "Tags Command",
    "Financial Status", "Fulfillment Status",
    "Billing: First Name", "Billing: Last Name", "Billing: Company",
    "Billing: Address 1", "Billing: Address 2", "Billing: City",
    "Billing: Province Code", "Billing: Country Code", "Billing: Zip",
    "Billing: Phone",
    "Shipping: First Name", "Shipping: Last Name", "Shipping: Company",
    "Shipping: Address 1", "Shipping: Address 2", "Shipping: City",
    "Shipping: Province Code", "Shipping: Country Code", "Shipping: Zip",
    "Shipping: Phone",
    "Line: Type", "Line: Title", "Line: SKU", "Line: Quantity", "Line: Price",
    "Line: Discount", "Line: Requires Shipping", "Line: Taxable",
    "Tax 1: Title", "Tax 1: Price",
    "Transaction: Kind", "Transaction: Status", "Transaction: Amount",
    "Transaction: Gateway", "Transaction: Processed At",
]


def address_fields(prefix, addr):
    return {
        f"{prefix}: First Name": addr.get("first_name", ""),
        f"{prefix}: Last Name": addr.get("last_name", ""),
        f"{prefix}: Company": addr.get("company", ""),
        f"{prefix}: Address 1": addr.get("address_1", ""),
        f"{prefix}: Address 2": addr.get("address_2", ""),
        f"{prefix}: City": addr.get("city", ""),
        f"{prefix}: Province Code": addr.get("state", ""),
        f"{prefix}: Country Code": addr.get("country", ""),
        f"{prefix}: Zip": addr.get("postcode", ""),
        f"{prefix}: Phone": addr.get("phone", ""),
    }


def main():
    orders = json.loads((DATA_DIR / "orders.json").read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "matrixify_orders.csv"

    order_count = 0
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()

        for order in orders:
            status = order.get("status", "")
            if status in ("checkout-draft", "trash"):
                continue
            name = f"#W{order.get('number', order['id'])}"
            processed_at = (order.get("date_paid") or order.get("date_created") or "")
            billing = order.get("billing", {})
            shipping = order.get("shipping", {}) or billing

            head = {
                "Name": name,
                "Command": "NEW",
                "Send Receipt": "FALSE",
                "Processed At": processed_at,
                "Cancelled At": order.get("date_modified", "") if status == "cancelled" else "",
                "Currency": order.get("currency", "USD"),
                "Email": billing.get("email", ""),
                "Phone": billing.get("phone", ""),
                "Note": order.get("customer_note", ""),
                "Tags": "woocommerce-import",
                "Tags Command": "REPLACE",
                "Financial Status": FINANCIAL_STATUS.get(status, "paid"),
                "Fulfillment Status": FULFILLMENT_STATUS.get(status, ""),
            }
            head.update(address_fields("Billing", billing))
            head.update(address_fields("Shipping", shipping))

            first = True
            for item in order.get("line_items", []):
                qty = item.get("quantity", 1) or 1
                row = dict(head) if first else {"Name": name}
                row.update({
                    "Line: Type": "Line Item",
                    "Line: Title": item.get("name", ""),
                    "Line: SKU": item.get("sku", ""),
                    "Line: Quantity": str(qty),
                    "Line: Price": f"{float(item.get('subtotal', 0)) / qty:.2f}",
                    "Line: Discount": f"{float(item.get('subtotal', 0)) - float(item.get('total', 0)):.2f}",
                    "Line: Requires Shipping": "TRUE",
                    "Line: Taxable": "TRUE",
                })
                tax = float(item.get("total_tax", 0) or 0)
                if tax:
                    row["Tax 1: Title"] = "Tax"
                    row["Tax 1: Price"] = f"{tax:.2f}"
                writer.writerow(row)
                first = False

            for ship in order.get("shipping_lines", []):
                row = dict(head) if first else {"Name": name}
                row.update({
                    "Line: Type": "Shipping Line",
                    "Line: Title": ship.get("method_title", "Shipping"),
                    "Line: Price": ship.get("total", "0"),
                })
                writer.writerow(row)
                first = False

            total = float(order.get("total", 0) or 0)
            if total and status in ("processing", "completed", "refunded"):
                writer.writerow({
                    "Name": name,
                    "Transaction: Kind": "sale",
                    "Transaction: Status": "success",
                    "Transaction: Amount": f"{total:.2f}",
                    "Transaction: Gateway": order.get("payment_method_title", "") or "imported",
                    "Transaction: Processed At": processed_at,
                })
            order_count += 1

    print(f"Wrote {order_count} orders -> {out_path}")
    print("Import with the Matrixify app on Shopify (matrixify.app).")


if __name__ == "__main__":
    main()

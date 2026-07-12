import frappe


def restore_manual_rate(doc, method):
    """Re-applies each BOM Item's custom_manual_rate after ERPNext's own
    calculate_cost() (run in BOM.validate) overwrites rate/amount based on
    rm_cost_as_per (Valuation Rate / Last Purchase Rate / Price List).
    CaratDesk sends custom_manual_rate = the rate actually agreed with the
    Supplier, and it must win over the auto-fetched rate.
    """
    changed = False
    for item in doc.items:
        manual_rate = item.get("custom_manual_rate")
        if manual_rate and item.rate != manual_rate:
            new_amount = item.qty * manual_rate
            item.db_set("rate", manual_rate, update_modified=False)
            item.db_set("base_rate", manual_rate, update_modified=False)
            item.db_set("amount", new_amount, update_modified=False)
            item.db_set("base_amount", new_amount, update_modified=False)
            changed = True

    if changed:
        total = sum((i.get("custom_manual_rate") or i.rate) * i.qty for i in doc.items)
        doc.db_set("total_cost", total, update_modified=False)
        doc.db_set("raw_material_cost", total, update_modified=False)

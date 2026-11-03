"""Casos sintéticos mínimos para verificar reglas de auditoría, no para entrenar."""

from pathlib import Path
import runpy

import pytest


MODULE = runpy.run_path(str(Path(__file__).parents[1] / "data" / "audit_meituan.py"))


def row(order_id="order-test", waybill_id="waybill-test", **changes):
    start = 1665964800
    result = {field: "1" for field in MODULE["REQUIRED"]}
    result.update(
        order_id=order_id, waybill_id=waybill_id, dt="20221017",
        is_prebook="0", is_weekend="0", is_courier_grabbed="1",
        platform_order_time=str(start), order_push_time=str(start + 1),
        dispatch_time=str(start + 2), grab_time=str(start + 3),
        fetch_time=str(start + 4), arrive_time=str(start + 60),
    )
    result.update(changes)
    return result


def test_rejected_attempt_is_not_counted_as_an_extra_delivery():
    report = MODULE["audit_rows"]([
        row(waybill_id="rejected", arrive_time="0", grab_time="0", fetch_time="0", is_courier_grabbed="0"),
        row(waybill_id="completed"),
    ])
    assert report["raw"]["rows"] == 2
    assert report["raw"]["distinct_orders"] == 1
    assert report["cohort_proposal"]["eligible_orders"] == 1
    assert report["cohort_proposal"]["duration"]["mean_minutes"] == 1


def test_changed_destination_excludes_ambiguous_order():
    report = MODULE["audit_rows"]([
        row(waybill_id="first", arrive_time="0", recipient_lng="2"),
        row(waybill_id="last"),
    ])
    assert report["raw"]["orders_with_conflicting_quote_fields"] == 1
    assert report["cohort_proposal"]["excluded_orders_by_first_reason"] == {"conflicting_quote_fields": 1}
    assert report["decision"] == "BLOQUEADO"


def test_separates_reservations_missing_delivery_and_invalid_timeline():
    report = MODULE["audit_rows"]([
        row("reserved", "a", is_prebook="1"),
        row("missing", "b", arrive_time="0"),
        row("negative", "c", arrive_time="-5"),
        row("reversed", "d", arrive_time="1665964799"),
        row("valid", "e"),
    ])
    excluded = report["cohort_proposal"]["excluded_orders_by_first_reason"]
    assert excluded == {"prebook_separate_scope": 1, "missing_completion": 2, "invalid_completed_timeline": 1}
    assert report["cohort_proposal"]["eligible_orders"] == 1
    assert report["raw"]["invalid_completed_target"] == 1


def test_integer_parser_does_not_truncate_or_repair_invalid_strings():
    with pytest.raises(ValueError, match="entero"):
        MODULE["audit_rows"]([row(platform_order_time="12.5")])
    with pytest.raises(ValueError, match="Indicador"):
        MODULE["audit_rows"]([row(is_prebook="2")])


def test_two_completed_attempts_are_not_chosen_arbitrarily():
    report = MODULE["audit_rows"]([row(waybill_id="a"), row(waybill_id="b")])
    assert report["cohort_proposal"]["excluded_orders_by_first_reason"] == {"multiple_completions": 1}
    assert report["decision"] == "BLOQUEADO"


def test_empty_data_and_duplicate_waybill_block_approval():
    empty = MODULE["audit_rows"]([])
    assert empty["decision"] == "BLOQUEADO"
    assert empty["cohort_proposal"]["duration"]["mean_minutes"] is None
    duplicate = MODULE["audit_rows"]([row("first"), row("second")])
    assert duplicate["raw"]["duplicate_waybill_ids"] == 1
    assert duplicate["decision"] == "BLOQUEADO"

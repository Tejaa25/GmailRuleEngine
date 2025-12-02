from datetime import datetime, timedelta, timezone
from database.models import Email
from rules import ConditionCreator, RuleLoader


def check_condition(email, condtion_dict):
    condtion = ConditionCreator.create(condition_dict=condtion_dict)
    return condtion.evaluate(email=email)


def check_rule(email, rule_dict):
    rule = RuleLoader().get_rule_obj(rule_dict=rule_dict)
    return rule.matches(email=email)


def create_test_email(sender="test@example.com", subject="Test", message="Body", days_ago=0):
    received = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return Email(
        id="test123",
        sender=sender,
        subject=subject,
        message=message,
        received_at=received,
        is_read=False,
        processed=False
    )
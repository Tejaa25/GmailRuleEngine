import pytest
from tests.common import create_test_email, check_condition, check_rule


class TestStringConditions:
    """string-based conditions (sender, subject, message)."""
    
    def test_contains_single_value(self):
        """single value."""

        email = create_test_email(sender="user@example.com")
        condition = {
            "field": "sender",
            "predicate": "contains",
            "value": "@example.com"
        }
        assert check_condition(email, condition) is True
    
    def test_contains_multiple_values(self):
        """list of values (OR logic)."""

        email = create_test_email(subject="URGENT: Please respond")
        condition = {
            "field": "subject",
            "predicate": "contains",
            "value": ["urgent", "important", "asap"]
        }
        assert check_condition(email, condition) is True
    
    def test_does_not_contain(self):
        """does_not_contain predicate."""

        email = create_test_email(message="Important update")
        condition = {
            "field": "message",
            "predicate": "does_not_contain",
            "value": "spam"
        }
        assert check_condition(email, condition) is True
    
    def test_equals(self):
        """equals predicate."""

        email = create_test_email(sender="admin@company.com")
        condition = {
            "field": "sender",
            "predicate": "equals",
            "value": "admin@company.com"
        }
        assert check_condition(email, condition) is True
    
    def test_not_equals(self):
        """not_equals predicate."""

        email = create_test_email(sender="user@example.com")
        condition = {
            "field": "sender",
            "predicate": "not_equals",
            "value": "spam@example.com"
        }
        assert check_condition(email, condition) is True

class TestDateConditions:
    """date-based conditions (received_at)."""
    
    def test_less_than_days_true(self):
        """less_than with days - should match recent email."""

        email = create_test_email(days_ago=3)
        condition = {
            "field": "received_at",
            "predicate": "less_than",
            "value": 7,
            "unit": "days"
        }
        assert check_condition(email, condition) is True
    
    def test_less_than_days_false(self):
        """less_than with days - should not match old email."""

        email = create_test_email(days_ago=10)
        condition = {
            "field": "received_at",
            "predicate": "less_than",
            "value": 7,
            "unit": "days"
        }
        assert check_condition(email, condition) is False
    
    def test_greater_than_days(self):
        """greater_than with days - should match old email."""

        email = create_test_email(days_ago=10)
        condition = {
            "field": "received_at",
            "predicate": "greater_than",
            "value": 7,
            "unit": "days"
        }
        assert check_condition(email, condition) is True
    
    def test_less_than_months(self):
        """less_than with months."""

        email = create_test_email(days_ago=15)  # ~2 weeks
        condition = {
            "field": "received_at",
            "predicate": "less_than",
            "value": 1,
            "unit": "months"
        }
        assert check_condition(email, condition) is False
    
    def test_greater_than_months(self):
        """greater_than with months."""

        email = create_test_email(days_ago=60)  # ~2 months
        condition = {
            "field": "received_at",
            "predicate": "greater_than",
            "value": 1,
            "unit": "months"
        }
        assert check_condition(email, condition) is True

class TestRuleMatching:
    """complete rule matching with multiple conditions."""
    
    def test_all_predicate_all_match(self):
        """ALL predicate when all conditions match."""

        email = create_test_email(
            sender="newsletter@company.com",
            subject="Weekly Newsletter",
            days_ago=10
        )
        rule = {
            "predicate": "All",
            "conditions": [
                {"field": "sender", "predicate": "contains", "value": "newsletter"},
                {"field": "subject", "predicate": "contains", "value": "Weekly"},
                {"field": "received_at", "predicate": "greater_than", "value": 7, "unit": "days"}
            ],
            "actions": [{"action": "mark_as_read"}]
        }
        
        assert check_rule(email, rule) is True
    
    def test_all_predicate_one_fails(self):
        """ALL predicate when one condition doesn't match."""

        email = create_test_email(
            sender="newsletter@company.com",
            subject="Weekly Newsletter",
            days_ago=3  # Less than 7 days - condition will fail
        )
        rule = {
            "predicate": "All",
            "conditions": [
                {"field": "sender", "predicate": "contains", "value": "newsletter"},
                {"field": "subject", "predicate": "contains", "value": "Weekly"},
                {"field": "received_at", "predicate": "greater_than", "value": 7, "unit": "days"}
            ],
            "actions": [{"action": "mark_as_read"}]
        }
        assert check_rule(email, rule) is False
    
    def test_any_predicate_one_matches(self):
        """ANY predicate when at least one condition matches."""

        email = create_test_email(
            sender="user@example.com",
            subject="URGENT: Action Required"
        )
        rule = {
            "predicate": "Any",
            "conditions": [
                {"field": "subject", "predicate": "contains", "value": ["urgent", "important"]},
                {"field": "sender", "predicate": "contains", "value": "@vip.com"}
            ],
            "actions": [{"action": "move_message", "destination": "Important"}]
        }
        assert check_rule(email, rule) is True
    
    def test_any_predicate_none_match(self):
        """ANY predicate when no conditions match."""

        email = create_test_email(
            sender="user@example.com",
            subject="Regular message"
        )
        rule = {
            "predicate": "Any",
            "conditions": [
                {"field": "subject", "predicate": "contains", "value": ["urgent", "important"]},
                {"field": "sender", "predicate": "contains", "value": "@vip.com"}
            ],
            "actions": [{"action": "move_message", "destination": "Important"}]
        }
        assert check_rule(email, rule) is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

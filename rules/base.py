from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
from datetime import datetime

from database import Email


class PredicateType(str, Enum):
    """Supported predicate types."""

    ALL = "All"
    ANY = "Any"


class FieldType(str, Enum):
    """Email fields that can be used in conditions."""

    SENDER = "sender"
    SUBJECT = "subject"
    MESSAGE = "message"
    RECEIVED_AT = "received_at"


class Condition(ABC):
    """This is the abstract class for rule conditions."""

    def __init__(self, field: str, predicate: str, value: Any):
        self.field = field
        self.predicate = predicate
        self.value = value

    @abstractmethod
    def evaluate(self, email: Email):
        pass

    def get_field_value(self, email: Email):
        return getattr(email, self.field, None)


class StringCondition(Condition):

    def evaluate(self, email: Email) -> bool:

        field_value = self.get_field_value(email)
        if field_value is None:
            return False
        field_value = str(field_value).lower()
        values = self.value if isinstance(self.value, list) else [self.value]
        values = [str(v).lower() for v in values]

        if self.predicate == "contains":
            return any(v in field_value for v in values)
        elif self.predicate == "does_not_contain":
            return all(v not in field_value for v in values)
        elif self.predicate == "equals":
            return field_value in values
        elif self.predicate == "not_equals":
            return field_value not in values
        return False


class DateCondition(Condition):

    def __init__(self, field: str, predicate: str, value: int, unit: str):
        super().__init__(field, predicate, value)
        self.unit = unit # Unit will be (days, months)

    def evaluate(self, email: Email) -> bool:

        field_value = self.get_field_value(email)
        if not isinstance(field_value, datetime):
            return False

        now = datetime.now(field_value.tzinfo or None)
        if self.unit == "days":
            delta = (now - field_value).days
        elif self.unit == "months":
            total_year_diff = (now.year - field_value.year)
            delta = total_year_diff * 12 + (now.month - field_value.month)
        else:
            return False

        if self.predicate == "less_than":
            return delta < self.value
        elif self.predicate == "greater_than":
            return delta > self.value
        return False


class Rule:
    """This class repr a single rule with conditions & actions."""

    def __init__(self, predicate, conditions, actions, description):
        self.predicate = predicate
        self.conditions = conditions
        self.actions = actions
        self.description = description

    def matches(self, email: Email) -> bool:
        """Check if the email matching this rule."""

        if not self.conditions:
            return False
        if self.predicate == PredicateType.ALL:
            return all([condition.evaluate(email) for condition in self.conditions])
        else:
            # Assuming the predicate is "any".
            for condition in self.conditions:
                if condition.evaluate(email):
                    return True
            return False


class ConditionCreator:

    @staticmethod
    def create(condition_dict: dict):
        """Create condition subclass from the given dictionary."""

        field = condition_dict.get("field")
        predicate = condition_dict.get("predicate")
        value = condition_dict.get("value")
        if not all([field, predicate, value is not None]):
            raise ValueError(f"Invalid conditions: {condition_dict}")

        if "unit" in condition_dict: # Date conditions have unit
            unit = condition_dict["unit"]
            return DateCondition(field, predicate, value, unit)
        else:
            return StringCondition(field, predicate, value)

import json
from jsonschema import validate, ValidationError

from .base import Rule, ConditionCreator, PredicateType
from config import Config
from utils import get_logger

logger = get_logger(__name__)


RULE_SCHEMA = {
    "type": "object",
    "properties": {
        "rules": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["predicate", "conditions", "actions"],
                "properties": {
                    "description": {"type": "string"},
                    "predicate": {"type": "string", "enum": ["All", "Any"]},
                    "conditions": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["field", "predicate", "value"],
                            "properties": {
                                "field": {
                                    "type": "string",
                                    "enum": [
                                        "sender",
                                        "subject",
                                        "message",
                                        "received_at",
                                    ],
                                },
                                "predicate": {
                                    "type": "string",
                                    "enum": [
                                        "contains",
                                        "does_not_contain",
                                        "equals",
                                        "not_equals",
                                        "less_than",
                                        "greater_than",
                                    ],
                                },
                                "value": {},
                                "unit": {"type": "string", "enum": ["days", "months"]},
                            },
                        },
                    },
                    "actions": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["action"],
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": [
                                        "mark_as_read",
                                        "mark_as_unread",
                                        "move_message",
                                    ],
                                },
                                "destination": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }
    },
    "required": ["rules"],
}


class RuleLoader:
    """Loads rules from JSON file."""

    def __init__(self, gmail_client=None):
        self.gmail_client = gmail_client
        self.rules_file = Config.RULES_FILE
        self._cached_rules = None

    def load_rules(self):
        """Load rules from JSON."""

        if self._cached_rules is not None:
            return self._cached_rules
        logger.info(f"Loading rules from {self.rules_file}")
        if not self.rules_file.exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_file}.")
        try:
            with self.rules_file.open("r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in rules file: {e}")

        try:
            validate(instance=data, schema=RULE_SCHEMA)
        except ValidationError as e:
            raise ValidationError(f"Rule validation failed: {e.message}")

        rules = []
        for idx, rule_dict in enumerate(data.get("rules", [])):
            try:
                rule = self.get_rule_obj(rule_dict)
                rules.append(rule)
            except Exception as e:
                logger.error(f"Failed to parse rule {idx + 1}: {e}")

        logger.info(f"Loaded {len(rules)} rules successfully")
        self._cached_rules = rules
        return rules

    def get_rule_obj(self, rule_dict: dict) -> Rule:
        """Convert dictionary into Rule object."""

        predicate = PredicateType(rule_dict["predicate"])
        conditions = []
        for cond_dict in rule_dict["conditions"]:
            try:
                condition = ConditionCreator.create(cond_dict)
                conditions.append(condition)
            except Exception as e:
                logger.warning(f"Skipping invalid condition: {e}")

        if not conditions:
            raise ValueError("Rule must have at least one valid condition")

        actions = rule_dict["actions"]
        for action in actions:
            if action["action"] == "move_message":
                if "destination" not in action:
                    raise ValueError("move_message action requires 'destination' field")
                if self.gmail_client:
                    self.gmail_client.get_or_create_label(action["destination"])

        return Rule(
            predicate=predicate,
            conditions=conditions,
            actions=actions,
            description=rule_dict.get("description", ""),
        )

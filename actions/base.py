# Global action registry
_action_registry = {}

def register_action(name: str):
    """Decorator to register action."""

    def decorator(func):
        _action_registry[name] = func
        return func

    return decorator

def get_action(name: str):
    return _action_registry.get(name)

def list_actions():
    return list(_action_registry.keys())

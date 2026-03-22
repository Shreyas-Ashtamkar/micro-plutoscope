class SingletonMeta(type):
    """Metaclass for singleton pattern."""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        """Return existing instance or create new one."""
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
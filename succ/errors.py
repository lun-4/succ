class HHApiError(Exception):
    """Hypnohub API Error."""
    pass


class ShutdownClient(Exception):
    """Client wants to shutdown."""
    pass

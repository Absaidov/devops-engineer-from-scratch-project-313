from .debug import router as debug_router
from .links import router as links_router
from .ping import router as ping_router

__all__ = ["debug_router", "links_router", "ping_router"]

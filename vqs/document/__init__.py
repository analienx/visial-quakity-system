"""Word lane: pagination spike harness plus OOXML structure inspection."""
from .inspect import inspect_docx
from .render import check_backend_equivalence, word_spike_readiness

__all__ = ["check_backend_equivalence", "inspect_docx", "word_spike_readiness"]

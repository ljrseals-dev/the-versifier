"""The Versifier (Il Versificatore): an homage to Primo Levi's poetry machine."""
from .engine import compose, fault_plea, prose_memo, REGISTERS, FORMS, ERAS, Poem

__all__ = ["compose", "fault_plea", "prose_memo", "REGISTERS", "FORMS", "ERAS", "Poem"]
__version__ = "1.0.0"

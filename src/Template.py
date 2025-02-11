from abc import ABC, abstractmethod

class Template(ABC):
    """An abstract class for creating a/some template(s)."""

    @abstractmethod
    def write(self):
        """Write the template to a file."""
        
        pass
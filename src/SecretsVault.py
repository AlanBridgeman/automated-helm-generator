from .Template import Template

class SecretsVault(Template):
    def __init__(self, type: str):
        super().__init__()

        self.type = type
    
    def write(self):
        pass
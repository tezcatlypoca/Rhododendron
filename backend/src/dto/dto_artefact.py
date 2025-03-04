from dataclasses import dataclass

@dataclass(repr=True, eq=True, frozen=True)
class Artefact:
    id: str
    type: str # 'code' | 'doc' | 'test'
    content: str
    createur: str
    version: str

    def __post_init__(self):
        if not self.is_valid_content(self.content):
            raise ValueError("Content cannot be empty")

    @staticmethod
    def is_valid_content(content: str) -> bool:
        return bool(content.strip())

# END CLASS
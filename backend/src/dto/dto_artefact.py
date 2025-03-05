from dataclasses import dataclass

@dataclass(repr=True, eq=True, frozen=True)
class Artefact:
    id: str
    type: str # 'code' | 'doc' | 'test'
    content: str
    creator: str
    version: str

    def __post_init__(self):
        if not self.is_valid_content(self.content):
            raise ValueError("Content cannot be empty")
        
        if not self.is_valid_type(self.type):
            raise ValueError("Type cannot be empty")
        
        if not self.is_valid_code(self.type):
            raise ValueError("Type should be a code like: 'code' | 'doc' | 'test'")
        
        if not self.is_valid_creator(self.creator):
            raise ValueError("Creator cannot be empty")
    # END FUNCTION

    @staticmethod
    def is_valid_type(type: str) -> bool:
        return bool(type.strip())
    
    @staticmethod
    def is_valid_code(type: str) -> bool:
        return (type == 'code') or (type == 'doc') or (type == 'test')

    @staticmethod
    def is_valid_content(content: str) -> bool:
        return bool(content.strip())
    
    @staticmethod
    def is_valid_creator(creator: str) -> bool:
        return bool(creator.strip())

# END CLASS
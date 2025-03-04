from dataclasses import dataclasses
from src.agents.Agent import Agent

@dataclasses
class ProjetDTO(repr=True, eq=True):
    _id: str
    name: str
    description: str
    instruments: list[Agent]
    historical: str # A réfléchir pour utiliser mieux et plus opti qu'une str comme moyen de stocker l'historique du orchestre
    
# END CLASS
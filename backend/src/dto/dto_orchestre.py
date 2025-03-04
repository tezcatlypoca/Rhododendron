from dataclasses import dataclass
from src.agents.Agent import Agent
from dto_projet import Projet
from dto_role import *
from src.settings import MODEL_NAME

@dataclass
class OrchestreDTO(repr=True, eq=True):
    _id: str
    name: str
    template: str
    description: str
    instruments: list[Agent]
    projets: list[Projet]
    MAX_PROJECT: int = None # Nombre limite de projet dans un orchestre
    current_project: int = None # Nombre actuel de projet créé dans l'orchestre
# END CLASS


@dataclass
class OrchestreClassique(Orchestre):
    def __init__(self):
        super.__init__(
            name = 'Classique Orchestre',
            template = 'classic',
            description = 'Orchestre paramétré avec un agent généraliste. Prêts à échanger sur n\'importe quels sujets',
            instruments = [Agent('IA classique', ClassicRole(), MODEL_NAME)],
            projets = []
        )
# END CLASS

@dataclass
class OrchestreDeveloppement(Orchestre):
    def __init__(self):
        super.__init__(
            name = 'Orchestre Developpement',
            template = 'Developpement',
            description = 'Orchestre paramétré avec une équipe d\'agents spécialisés en développement.\nAgents affiliés: Manager, Developer, Tester',
            instruments = [
                        Agent('Manager', ManagerRole(), MODEL_NAME),
                        Agent('Developpeur', DeveloperRole(), MODEL_NAME),
                        Agent('Testeur', TesterRole(), MODEL_NAME)
                           ],
            projets = []
        )
# END CLASS
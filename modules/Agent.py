import logging
from typing import List

from modules.MistralApiClient import MistralApiClient


class Agent:
	"""
	Classe de base représentant un agent capable d'effectuer une tâche.
	"""
	def __init__(self, name: str, apiClient: MistralApiClient):
		self.name = name
		self.apiClient = apiClient
		self.logger = logging.getLogger(__name__)

	def performTask(self, taskDescription: str) -> str:
		"""
		Effectue la tâche et retourne le résultat.
		"""
		prompt = f"{self.name} doit {taskDescription}"
		self.logger.info(f"{self.name} réalise la tâche : {taskDescription}")
		result = self.apiClient.callModel(prompt)
		self.logger.info(f"Résultat de {self.name} : {result}")
		return result

class MotherAgent(Agent):
	"""
	Agent mère qui détermine le nombre d'agents enfants à créer et délègue les tâches.
	"""
	def __init__(self, name: str, apiClient: MistralApiClient):
		super().__init__(name, apiClient)
		self.childAgents: List[Agent] = []

	def determineNumberOfAgents(self, task: str) -> int:
		"""
		Détermine le nombre d'agents nécessaires en utilisant l'API.
		"""
		prompt = (
			f"{self.name} doit décider combien d'agents sont nécessaires pour accomplir la tâche suivante : "
			f"'{task}'. Réponds uniquement par un nombre entier."
		)
		response = self.apiClient.callModel(prompt, maxTokens=10)
		try:
			number = int(response.strip())
			self.logger.info(f"{self.name} a déterminé le nombre d'agents : {number}")
			return number
		except ValueError:
			self.logger.error(f"Nombre invalide retourné par l'API : '{response}'. Utilisation de 1 comme valeur par défaut.")
			return 1

	def spawnChildAgents(self, number: int) -> None:
		"""
		Crée le nombre spécifié d'agents enfants.
		"""
		self.childAgents = [
			Agent(name=f"ChildAgent_{i+1}", apiClient=self.apiClient)
			for i in range(number)
		]
		self.logger.info(f"{self.name} a créé {number} agents enfants.")

	def delegateTasks(self, task: str) -> None:
		"""
		Délègue la tâche aux agents enfants.
		"""
		self.logger.info(f"{self.name} délègue la tâche '{task}' aux agents enfants.")
		for agent in self.childAgents:
			result = agent.performTask(task)
			self.logger.info(f"Résultat de {agent.name} : {result}")
import logging
import json
from typing import List
from modules.MistralApiClient import MistralApiClient
from modules.PromptManager import PromptManager

class Agent:
	"""
	Classe de base représentant un agent capable d'effectuer une tâche.
	"""
	def __init__(self, name: str, apiClient: MistralApiClient, promptManager: PromptManager = None) -> None:
		self.name: str = name
		self.apiClient: MistralApiClient = apiClient
		self.promptManager: PromptManager = promptManager
		self.logger = logging.getLogger(__name__)

	def performTask(self, taskDescription: str) -> str:
		"""
		Effectue la tâche et retourne le résultat.
		"""
		if self.promptManager:
			prompt: str = self.promptManager.buildPrompt(self.name, taskDescription)
		else:
			prompt = f"{self.name} doit {taskDescription}"
		self.logger.info(f"{self.name} réalise la tâche : {taskDescription}")
		result: str = self.apiClient.callModel(prompt)
		self.logger.info(f"Résultat de {self.name} : {result}")
		return result

class MotherAgent(Agent):
	"""
	Agent mère qui détermine le nombre d'agents enfants à créer et délègue les tâches.
	"""
	def __init__(self, name: str, apiClient: MistralApiClient, promptManager: PromptManager = None) -> None:
		super().__init__(name, apiClient, promptManager)
		self.childAgents: List[Agent] = []

	def determineNumberOfAgents(self, taskDescription: str) -> int:
		"""
		Détermine le nombre d'agents nécessaires en utilisant l'API.
		La réponse doit être un JSON de la forme {"agentCount": X}.
		"""
		if self.promptManager:
			prompt: str = self.promptManager.buildPrompt(
				self.name,
				f"Détermine le nombre d'agents nécessaires pour accomplir la tâche suivante en répondant par un JSON {{'agentCount': nombre}} : '{taskDescription}'"
			)
		else:
			prompt = (f"{self.name} doit décider combien d'agents sont nécessaires pour accomplir la tâche suivante : "
					  f"'{taskDescription}'. Réponds uniquement par un nombre entier.")
		response: str = self.apiClient.callModel(prompt, maxTokens=50)
		try:
			# Correction des guillemets pour respecter le format JSON
			responseJson = json.loads(response.replace("'", "\""))
			agentCount = int(responseJson.get("agentCount", 1))
			self.logger.info(f"{self.name} a déterminé le nombre d'agents : {agentCount}")
			return agentCount
		except (json.JSONDecodeError, ValueError, AttributeError) as e:
			self.logger.error(f"Erreur lors du parsing de la réponse JSON '{response}': {e}. Utilisation de 1 comme valeur par défaut.")
			return 1

	def spawnChildAgents(self, number: int) -> None:
		"""
		Crée le nombre spécifié d'agents enfants.
		"""
		self.childAgents = [
			Agent(name=f"ChildAgent{i+1}", apiClient=self.apiClient, promptManager=self.promptManager)
			for i in range(number)
		]
		self.logger.info(f"{self.name} a créé {number} agents enfants.")

	def delegateTasks(self, taskDescription: str) -> None:
		"""
		Délègue la tâche aux agents enfants.
		"""
		self.logger.info(f"{self.name} délègue la tâche '{taskDescription}' aux agents enfants.")
		for agent in self.childAgents:
			result: str = agent.performTask(taskDescription)
			self.logger.info(f"Résultat de {agent.name} : {result}")

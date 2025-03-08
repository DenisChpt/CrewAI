import logging
import json
import concurrent.futures

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
			prompt: str = self.promptManager.buildPrompt(self.name, taskDescription, role="Agent")
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
				f"Détermine le nombre d'agents nécessaires pour accomplir la tâche suivante. Réponds par un JSON correctement formaté avec des guillemets doubles, par exemple: {{\"agentCount\": 3}}. Tâche: '{taskDescription}'",
				role="MotherAgent"
			)
		else:
			prompt = (f"{self.name} doit décider combien d'agents sont nécessaires pour accomplir la tâche suivante : "
					  f"'{taskDescription}'. Réponds uniquement par un nombre entier.")
		response: str = self.apiClient.callModel(prompt, maxTokens=50)
		try:
			# Correction des guillemets et vérification du format JSON
			response_clean = response.replace("'", "\"")
			responseJson = json.loads(response_clean)
			if not isinstance(responseJson, dict):
				raise ValueError("La réponse JSON n'est pas un dictionnaire")
			agentCount = responseJson.get("agentCount")
			if not isinstance(agentCount, int):
				raise ValueError("La valeur de 'agentCount' n'est pas un entier")
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
		Délègue la tâche aux agents enfants en appelant leurs API en parallèle.
		"""
		self.logger.info(f"{self.name} délègue la tâche '{taskDescription}' aux agents enfants.")
		with concurrent.futures.ThreadPoolExecutor() as executor:
			future_to_agent = {executor.submit(agent.performTask, taskDescription): agent for agent in self.childAgents}
			for future in concurrent.futures.as_completed(future_to_agent):
				agent = future_to_agent[future]
				try:
					result: str = future.result()
					self.logger.info(f"Résultat de {agent.name} : {result}")
				except Exception as e:
					self.logger.error(f"Erreur lors de l'exécution de la tâche de {agent.name} : {e}")

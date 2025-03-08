import logging
import json
import concurrent.futures
from typing import List, Dict, Any
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
	Agent mère qui détermine le plan d'agents à créer (nombre et rôles) et délègue les tâches.
	"""
	def __init__(self, name: str, apiClient: MistralApiClient, promptManager: PromptManager = None) -> None:
		super().__init__(name, apiClient, promptManager)
		self.childAgents: List[Agent] = []

	def determineNumberOfAgents(self, taskDescription: str) -> Dict[str, Any]:
		"""
		Détermine le plan des agents nécessaires pour accomplir la tâche en utilisant l'API.
		La réponse doit être un JSON de la forme:
		{
			"agentCount": X,
			"agents": [
				{"name": "ChildAgent1", "role": "Fonction et contexte", "context": "Description..."},
				{"name": "ChildAgent2", "role": "Fonction et contexte", "context": "Description..."}
			]
		}
		"""
		if self.promptManager:
			prompt: str = self.promptManager.buildPrompt(
				self.name,
				f"Détermine le nombre d'agents nécessaires pour accomplir la tâche suivante et spécifie pour chacun leur fonction et leur contexte. "
				f"Réponds par un JSON correctement formaté avec des guillemets doubles, par exemple: "
				f"{{\"agentCount\": 2, \"agents\": [{{\"name\": \"ChildAgent1\", \"role\": \"Expert en architecture\", \"context\": \"Analyse et définition de l'architecture.\"}}, "
				f"{{\"name\": \"ChildAgent2\", \"role\": \"Développeur\", \"context\": \"Implémentation du code.\"}}]}}. Tâche: '{taskDescription}'",
				role="MotherAgent"
			)
		else:
			prompt = (f"{self.name} doit décider combien d'agents sont nécessaires pour accomplir la tâche suivante et définir leur rôle : "
					  f"'{taskDescription}'. Réponds par un nombre entier.")
		self.logger.info(f"{self.name} envoie le prompt pour déterminer le plan des agents : {prompt}")
		response: str = self.apiClient.callModel(prompt, maxTokens=150)
		self.logger.info(f"Réponse brute reçue: {response}")

		try:
			# Extraction du JSON à partir de la réponse (on recherche le premier '{' et le dernier '}')
			start_index = response.find('{')
			end_index = response.rfind('}') + 1
			if start_index == -1 or end_index == -1:
				raise ValueError("Aucun objet JSON trouvé dans la réponse")
			json_str = response[start_index:end_index]
			self.logger.debug(f"JSON extrait: {json_str}")

			responseJson = json.loads(json_str)
			if not isinstance(responseJson, dict):
				raise ValueError("La réponse JSON n'est pas un dictionnaire")

			agentCount = responseJson.get("agentCount")
			agents = responseJson.get("agents")

			if not isinstance(agentCount, int) or not isinstance(agents, list):
				raise ValueError("Le format du JSON est incorrect (agentCount ou agents manquant)")
			
			self.logger.info(f"{self.name} a déterminé le plan des agents : {agentCount} agents, détails: {agents}")
			return responseJson
		except (json.JSONDecodeError, ValueError, AttributeError) as e:
			self.logger.error(f"Erreur lors du parsing de la réponse JSON '{response}': {e}. Utilisation d'un plan par défaut avec un agent.")
			# Plan par défaut
			default_plan = {
				"agentCount": 1,
				"agents": [
					{"name": "ChildAgent1", "role": "Généraliste", "context": "Aucune spécificité fournie."}
				]
			}
			return default_plan

	def spawnChildAgents(self, agentPlan: Dict[str, Any]) -> None:
		"""
		Crée les agents enfants selon le plan fourni.
		"""
		agents_list = agentPlan.get("agents", [])
		self.childAgents = [
			Agent(name=agent_info.get("name", f"ChildAgent{i+1}"), apiClient=self.apiClient, promptManager=self.promptManager)
			for i, agent_info in enumerate(agents_list)
		]
		roles_info = ", ".join([f"{agent_info.get('name', f'ChildAgent{i+1}')} ({agent_info.get('role', 'sans rôle')})" 
								for i, agent_info in enumerate(agents_list)])
		self.logger.info(f"{self.name} a créé {len(self.childAgents)} agents enfants avec les rôles: {roles_info}")

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

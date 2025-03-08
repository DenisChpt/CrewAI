# File: modules/PromptManager.py

class PromptManager:
	"""
	Gère la construction des prompts en incluant un pré-prompt contextuel.
	"""
	def __init__(self, prePrompt: str) -> None:
		self.prePrompt: str = prePrompt

	def buildPrompt(self, agentName: str, taskDescription: str, role: str = None) -> str:
		"""
		Construit le prompt en incluant le pré-prompt et la tâche à réaliser.
		Si un rôle est spécifié, des instructions supplémentaires sont ajoutées.
		"""
		prompt = f"{self.prePrompt}\n\n"
		if role:
			if role == "MotherAgent":
				prompt += "[Rôle: Agent mère - veille à renvoyer des réponses JSON correctement formatées, par exemple: {\"agentCount\": 3}]\n"
			elif role == "Agent":
				prompt += "[Rôle: Agent - fournir une réponse modulaire et claire]\n"
			else:
				prompt += f"[Rôle: {role}]\n"
		prompt += f"{agentName} doit {taskDescription}"
		return prompt

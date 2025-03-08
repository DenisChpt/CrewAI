class PromptManager:
	"""
	Gère la construction des prompts en incluant un pré-prompt contextuel.
	"""
	def __init__(self, prePrompt: str) -> None:
		self.prePrompt: str = prePrompt

	def buildPrompt(self, agentName: str, taskDescription: str) -> str:
		"""
		Construit le prompt en incluant le pré-prompt et la tâche à réaliser.
		"""
		return f"{self.prePrompt}\n\n{agentName} doit {taskDescription}"

import logging
from config.config import config
from modules.MistralApiClient import MistralApiClient
from modules.Agent import MotherAgent
from modules.PromptManager import PromptManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
	# Chargement des paramètres depuis le fichier de configuration
	apiKey: str = config.get("apiKey")
	baseUrl: str = config.get("baseUrl")
	defaultMaxTokens: int = config.get("defaultMaxTokens")
	model: str = config.get("model")
	prePrompt: str = config.get("prePrompt")

	# Initialisation du client API et du gestionnaire de prompts
	client = MistralApiClient(apiKey=apiKey, baseUrl=baseUrl, defaultMaxTokens=defaultMaxTokens, model=model)
	promptManager = PromptManager(prePrompt=prePrompt)

	# Création de l'agent mère
	motherAgent = MotherAgent(name="MotherAgent", apiClient=client, promptManager=promptManager)

	# Exemple de description de tâche
	taskDescription: str = "générer un script python modulaire et bien structuré"
	
	# Détermination du plan des agents (nombre et rôles)
	agentPlan = motherAgent.determineNumberOfAgents(taskDescription)
	motherAgent.spawnChildAgents(agentPlan)
	motherAgent.delegateTasks(taskDescription)

if __name__ == "__main__":
	main()

import logging

from modules.MistralApiClient import MistralApiClient
from modules.Agent import MotherAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
	apiKey = "YOUR_API_KEY"
	client = MistralApiClient(apiKey=apiKey)

	mother = MotherAgent(name="MotherAgent", apiClient=client)
	taskDescription = "générer un script python modulaire et bien structuré"
	
	numAgents = mother.determineNumberOfAgents(taskDescription)
	mother.spawnChildAgents(numAgents)
	mother.delegateTasks(taskDescription)

if __name__ == "__main__":
	main()

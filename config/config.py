import os
import json

class Config:
	"""
	Classe pour charger la configuration depuis un fichier JSON.
	"""
	def __init__(self, configPath: str = os.path.join(os.path.dirname(__file__), "config.json")) -> None:
		with open(configPath, "r", encoding="utf-8") as file:
			self.config = json.load(file)

	def get(self, key: str, default=None):
		return self.config.get(key, default)

# Instance globale de configuration
config = Config()

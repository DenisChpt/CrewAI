import requests
import logging

class MistralApiClient:
	"""
	Client pour interagir avec l'API de Mistral.
	"""
	def __init__(self, apiKey: str, baseUrl: str = "https://api.mistral.ai"):
		self.apiKey = apiKey
		self.baseUrl = baseUrl
		self.logger = logging.getLogger(__name__)

	def callModel(self, prompt: str, model: str = "codestral-22b", maxTokens: int = 256) -> str:
		"""
		Envoie une requête à l'API Mistral et retourne le texte généré.
		"""
		endpoint = f"{self.baseUrl}/v1/generate"
		headers = {
			"Authorization": f"Bearer {self.apiKey}",
			"Content-Type": "application/json"
		}
		payload = {
			"model": model,
			"prompt": prompt,
			"max_tokens": maxTokens
		}
		try:
			response = requests.post(endpoint, headers=headers, json=payload)
			response.raise_for_status()
			data = response.json()
			return data.get("generated_text", "")
		except requests.RequestException as e:
			self.logger.error(f"Erreur lors de l'appel à l'API : {e}")
			return ""
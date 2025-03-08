import requests
import logging
from typing import Optional
import time

class MistralApiClient:
	"""
	Client pour interagir avec l'API de Mistral.
	"""
	def __init__(self, apiKey: str, baseUrl: str = "https://api.mistral.ai", defaultMaxTokens: int = 256, model: str = "codestral-22b") -> None:
		self.apiKey: str = apiKey
		self.baseUrl: str = baseUrl
		self.defaultMaxTokens: int = defaultMaxTokens
		self.model: str = model
		self.logger = logging.getLogger(__name__)

	def callModel(self, prompt: str, maxTokens: Optional[int] = None, timeout: int = 10, retries: int = 3) -> str:
		"""
		Envoie une requête à l'API Mistral et retourne le texte généré.
		Ajoute une gestion de timeout et de retries pour plus de robustesse.
		"""
		if maxTokens is None:
			maxTokens = self.defaultMaxTokens

		endpoint: str = f"{self.baseUrl}/v1/generate"
		headers = {
			"Authorization": f"Bearer {self.apiKey}",
			"Content-Type": "application/json"
		}
		payload = {
			"model": self.model,
			"prompt": prompt,
			"max_tokens": maxTokens
		}

		for attempt in range(1, retries + 1):
			try:
				response = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
				response.raise_for_status()
				data = response.json()
				if not isinstance(data, dict):
					raise ValueError("La réponse n'est pas un dictionnaire JSON.")
				return data.get("generated_text", "")
			except (requests.RequestException, ValueError) as e:
				self.logger.error(f"Erreur lors de l'appel à l'API (tentative {attempt}/{retries}) : {e}")
				if attempt < retries:
					time.sleep(2)  # Pause avant de réessayer
				else:
					return ""

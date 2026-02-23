__all__ = ["K3S_Client"]

from base64 import b64decode

from kubernetes import client, config
from kubernetes.client.models.v1_secret import V1Secret


class K3S_Client:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    def get_secret(self, name, namespace="default") -> dict[str, str]:
        try:
            secret = self.v1.read_namespaced_secret(name=name, namespace=namespace)
            if isinstance(secret, V1Secret) and isinstance((data := secret.data), dict):
                return {key: b64decode(value).decode() for key, value in data.items()}
            raise Exception(
                f"Failed to read secret: '{name}' from namespace '{namespace}'."
            )
        except Exception as e:
            return {"error": str(e)}

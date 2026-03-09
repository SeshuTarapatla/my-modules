from base64 import b64decode

from kubernetes import client, config


class Kubernetes:
    """A class for interacting with Kubernetes resources.

    This class provides methods to interact with Kubernetes secrets and other resources
    using the Kubernetes Python client library.
    """

    def __init__(self) -> None:
        """Initialize the Kubernetes client.

        Loads the kubeconfig and creates a CoreV1Api client instance for interacting
        with Kubernetes resources.
        """
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    def list_secrets(self) -> list[str]:
        """List all secret names in the default namespace.

        Returns:
            list[str]: A list of secret names in the default namespace.

        Example:
            >>> k8s = Kubernetes()
            >>> secrets = k8s.list_secrets()
            >>> print(secrets)
            ['secret1', 'secret2', 'secret3']
        """
        return [
            secret.metadata.name
            for secret in self.v1.list_namespaced_secret("default").items
        ]

    def get_secret(self, secret: str, namespace: str = "default") -> dict[str, str]:
        """Retrieve and decode a secret from Kubernetes.

        Args:
            secret (str): The name of the secret to retrieve.
            namespace (str, optional): The namespace where the secret is located.
                Defaults to "default".

        Returns:
            dict[str, str]: A dictionary containing the decoded secret data as key-value pairs.
                Returns an empty dictionary if the secret doesn't exist.

        Example:
            >>> k8s = Kubernetes()
            >>> secret_data = k8s.get_secret("my-secret")
            >>> print(secret_data)
            {'username': 'admin', 'password': 'secret123'}
        """
        if secret in self.list_secrets():
            secret_data = getattr(
                self.v1.read_namespaced_secret(name=secret, namespace=namespace), "data"
            )
            decoded_data = {
                key: b64decode(value).decode("utf-8")
                for key, value in secret_data.items()
            }
            return decoded_data
        else:
            return {}
    
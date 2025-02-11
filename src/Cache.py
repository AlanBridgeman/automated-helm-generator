from .Template import Template

class Cache (Template):
    def __init__(self, password: str, hostName: str, port: str, create: bool):
        """A class for creating a/some template(s) related to a cache server.

        Args:
            password (str): The password to access the cache server.
            hostName (str): The hostname of the cache server.
            port (str): The port of the cache server.
            create (bool): Whether or not to create the cache server as part of the Helm Chart deployment.
        """

        super().__init__()

        self.password = password
        self.hostName = hostName
        self.port = port
        self.create = create

    def write_generic_cache_templates(self, type: str, default_hostname: str):
        """Write the generic cache templates to a file.
        
        Args:
            type (str): The type of cache server. Relevant if the cache server is to be created as the default hostname will be used if the type matches with whats provided in the `values.yaml` file.
            default_hostname (str): The default hostname of the cache server. Used if the cache server is to be created and the type matches with whats provided in the `values.yaml` file.
        """

        # Create the configmap file that holds the hostname and port of the cache server
        with open('templates/cache-configmap.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: ConfigMap' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-cache-configmap' + '\n')
            f.write('  ' + 'namespace: {{ .Release.Namespace }}' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + '{{- if and (eq .Values.cache.type "' + type + '") (.Values.cache.create) }}' + '\n')
            f.write('  ' + f'hostname: {default_hostname}' + '\n')
            f.write('  ' + '{{- else }}' + '\n')
            f.write('  ' + 'hostname: {{ .Values.cache.hostname }}' + '\n')
            f.write('  ' + '{{- end }}' + '\n')
            f.write('  ' + 'port: {{ .Values.cache.port }}' + '\n')
        
        # Create the credentials secret file
        with open('templates/cache-credentials-secret.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-cache-credentials' + '\n')
            f.write('type: Opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'password: {{ .Values.cache.password | b64enc }}' + '\n')
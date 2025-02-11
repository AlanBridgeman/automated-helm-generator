from .Cache import Cache

class Redis (Cache):
    def __init__(self, password: str, create: bool = True, hostName: str = '{{ .Release.Name }}-redis', replicaCount: int = 1, port: str = '6379', tls_enabled: bool = False, tls_port: str = '6380', image: dict[str, str] = {}):
        """A class for creating a/some template(s) related to a Redis server.

        Args:
            password (str): The password to use to access the Redis instance.
            create (bool, Optional): Whether or not to create the Redis instance as part of the Helm Chart. Default True
            hostName (str, Optional): The hostname of the Redis instance. Default '{{ .Release.Name }}-redis'
            replicaCount (int, Optional): The number of replicas of the Redis instance. Default 1
            port (str, Optional): The port of the Redis instance. Default '6379'
            tls_enabled (bool, Optional): Whether or not to enable TLS for the Redis instance. Default False
            tls_port (str, Optional): The port of the Redis instance for TLS. Default '6380'
            image (dict[str, str], Optional): The image of the Redis instance. Default {}
        """

        super().__init__(password, hostName, port, create)

        self.replicaCount = replicaCount
        self.tls_enabled = tls_enabled
        self.tls_port = tls_port
        self.image = image

    def write(self):
        # Call parent class's method/function to write the generic cache templates
        super().write_generic_cache_templates('redis', '{{ .Release.Name }}-redis')
        
        # Create the Redis service file
        with open('templates/redis-service.yaml', 'w') as f:
            f.write('{{- if and (.Values.cache.type "redis") (.Values.cache.create) -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Service' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-redis' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: redis' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'ports:' + '\n')
            f.write('  ' + '  ' + '- port: {{ .Values.cache.port }}' + '\n')
            f.write('  ' + '  ' + '  ' + 'targetPort: {{ .Values.cache.port }}' + '\n')
            f.write('  ' + 'selector:' + '\n')
            f.write('  ' + '  ' + 'app: redis' + '\n')
            f.write('  ' + 'type: ClusterIP' + '\n')
            f.write('{{- end -}}')


        # Create the Redis deployment file
        with open('templates/redis-deployment.yaml', 'w') as f:
            f.write('{{- if and (.Values.cache.type "redis") (.Values.cache.create) -}}' + '\n')
            f.write('apiVersion: apps/v1' + '\n')
            f.write('kind: Deployment' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-redis' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: redis' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'replicas: {{ .Values.cache.replicaCount }}' + '\n')
            f.write('  ' + 'selector:' + '\n')
            f.write('  ' + '  ' + 'matchLabels:' + '\n')
            f.write('  ' + '  ' + '  ' + 'app: redis' + '\n')
            f.write('  ' + 'template:' + '\n')
            f.write('  ' + '  ' + 'metadata:' + '\n')
            f.write('  ' + '  ' + '  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'app: redis' + '\n')
            f.write('  ' + '  ' + 'spec:' + '\n')
            f.write('  ' + '  ' + '  ' + 'containers:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: redis' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'image: {{ .Values.cache.image.repository | default "bitnami/redis" }}:{{ .Values.cache.image.tag | default "7.0.5" }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'ports:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '- containerPort: {{ .Values.cache.port }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '{{- if .Values.cache.tls.enabled }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '- containerPort: {{ .Values.cache.tls.port }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '{{- end }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'env:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '- name: ALLOW_EMPTY_PASSWORD' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'value: "false"' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '- name: REDIS_PASSWORD' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-cache-credentials' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: password' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '- name: REDIS_DISABLE_COMMANDS' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'value: "FLUSHDB,FLUSHALL"' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '# TLS configuration' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '#- name: REDIS_TLS_ENABLED' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '#  value: "{{ .Values.cache.tls.enabled }}"' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '#- name: REDIS_TLS_AUTH_CLIENTS' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '#  value: "yes"' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '#- name: REDIS_TLS_PORT_NUMBER' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '#  value: "{{ .Values.cache.tls.port }}"' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'volumeMounts:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '- name: redis-data' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'mountPath: /bitnami/redis' + '\n')
            f.write('  ' + '  ' + '  ' + 'volumes:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: redis-data' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'emptyDir: {}' + '\n')
            f.write('{{- end -}}')
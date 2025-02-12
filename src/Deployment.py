from .Template import Template
from .NoSQL import NoSQL
from .ThirdPartyService import ThirdPartyService

class Deployment (Template):
    def __init__(self, image_repository: str, image_tag: str = 'v1.0.0', image_pull_policy: str = 'IfNotPresent', replica_count: int = 1, port: int = 8080, env: str = 'production', uses_oauth: bool = True, uses_db: bool = False, nosql: NoSQL | None = None, uses_cache: bool = False, third_party_services: list[ThirdPartyService] = [], **extra_env_vars: dict[str, str | dict[str, str]]):
        """A class for creating a/some template(s) related to the Deployment for the app.
        
        Args:
            image_repository (str): The repository of the image to be used for the Deployment.
            image_tag (str, Optional): The tag of the image to be used for the Deployment. Default 'v1.0.0'
            image_pull_policy (str, Optional): The image pull policy to be used for the Deployment. Default 'IfNotPresent'
            replica_count (int, Optional): The number of replicas of the app to be running. Default 1
            port (int, Optional): The port the app will be running on. Default 8080
            env (str, Optional): The environment the app will be running in. Default 'production'
            uses_oauth (bool, Optional): Whether or not OAuth is to be used. Determines if OAuth related environment variables need to be set on the Deployment. Default True
            uses_db (bool, Optional): Whether or not a database is to be used. Determines if database related environment variables need to be set on the Deployment. Default False
            nosql (NoSQL, Optional): The NoSQL template. If set, Determines if NoSQL database related environment variables need to be set on the Deployment. We require the object to get table names to set appropriate environment variables on the Deployment. Default None
            uses_cache (bool, Optional): Whether or not a cache server is to be used. Determines if cache related environment variables need to be set on the Deployment. Default False
            third_party_services (list[ThirdPartyService], Optional): The third party services to be used. Determines if third party service related environment variables need to be set on the Deployment. Default empty list (`[]`)
            extra_env_vars (dict[str, str | dict[str, str]]): Extra environment variables to be set on the Deployment. The key is the name of the environment variable and the value, if it's a string, is the value of the environment variable. If the value is a dictionary, than a file for the value as a secret or configmap is created and referenced by the environment variable.
        """
        
        super().__init__()

        self.image_repository = image_repository
        self.image_tag = image_tag
        self.image_pull_policy = image_pull_policy
        self.replica_count = replica_count
        self.env = env
        self.port = port
        self.uses_oauth = uses_oauth
        self.uses_db = uses_db
        self.nosql = nosql
        self.uses_cache = uses_cache
        self.third_party_services = third_party_services
        self.extra_env_vars = extra_env_vars
    
    def write(self):
        """Write the Deployment template to a file."""
        
        for value in self.extra_env_vars.values():
            if isinstance(value, dict):
                if value['type'] == 'Secret':
                    filename = value['name']
                    if filename.startswith('{{ .Release.Name }}'):
                        filename = filename.replace('{{ .Release.Name }}-', '')
                    
                    snake_case_name = filename.split('-')[0]
                    for token in filename.split('-'):
                        if token != snake_case_name:
                            snake_case_name += token.capitalize()

                    with open(f'templates/{filename}-secret.yaml', 'w') as f:
                        f.write('apiVersion: v1' + '\n')
                        f.write('kind: Secret' + '\n')
                        f.write('metadata:' + '\n')
                        f.write('  ' + f'name: {value["name"]}' + '\n')
                        f.write('type: Opaque' + '\n')
                        f.write('data:' + '\n')
                        f.write('  ' + f'{value["key"]}: ' + '{{ .Values.' + snake_case_name + ' | b64enc }}' + '\n')

        with open(f'templates/deployment.yaml', 'w') as f:
            f.write('apiVersion: apps/v1' + '\n')
            f.write('kind: Deployment' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'replicas: {{ .Values.replicaCount }}' + '\n')
            f.write('  ' + 'selector:' + '\n')
            f.write('  ' + '  ' + 'matchLabels:' + '\n')
            f.write('  ' + '  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('  ' + 'template:' + '\n')
            f.write('  ' + '  ' + 'metadata:' + '\n')
            f.write('  ' + '  ' + '  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('  ' + '  ' + 'spec:' + '\n')
            f.write('  ' + '  ' + '  ' + 'containers:' + '\n')
            f.write('  ' + '  ' + '  ' + '- name: {{ .Release.Name }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'image: {{ .Values.image.repository }}:{{ .Values.image.tag }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'imagePullPolicy: {{ .Values.image.pullPolicy }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'ports:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- containerPort: {{ .Values.container.port }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'env:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: NODE_ENV' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'value: {{ .Values.container.env }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: PORT' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'value: "{{ .Values.container.port }}"' + '\n')
            
            for key, value in self.extra_env_vars.items():
                # Check if the value is a dictionary or a string
                if isinstance(value, dict):
                    f.write('  ' + '  ' + '  ' + '  ' + f'- name: {key.upper()}' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                    if value['type'] == 'Secret':
                        f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
                    elif value['type'] == 'ConfigMap':
                        f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: ' + value['name'] + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: ' + value['key'] + '\n')
                else:
                    f.write('  ' + '  ' + '  ' + '  ' + f'- name: {key.upper()}' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + f'value: {value}' + '\n')
            
            if self.uses_oauth:
                f.write('  ' + '  ' + '  ' + '  ' + '# OAuth Implementation Stuff' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: BASE_APP_URL' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: base-app-url' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: APP_ABBRV' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: app-abbreviation' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: APP_NAME' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: app-name' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: SERVICE_NAME' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: service-name' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: DEV_PORT' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: dev-port' + '\n')
            
            if self.uses_db:
                f.write('  ' + '  ' + '  ' + '  ' + '# Database credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: DB_HOST' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-host' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: DB_NAME' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-name' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: DB_PASSWORD' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-password' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: password' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: DB_PORT' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-port' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: DB_USER' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-user' + '\n')
            
            if self.nosql is not None:
                f.write('  ' + '  ' + '  ' + '  ' + '# NoSQL Credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '{{- if eq .Values.nosql.type "mongodb" }}' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: STORAGE_ACCOUNT_CONNECTION_STRING' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-mongo-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: connection-string' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '{{- else if eq .Values.nosql.type "azure" }}' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: STORAGE_ACCOUNT_KEY' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-azure-tables-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: key' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: STORAGE_ACCOUNT_NAME' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-azure-tables-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: name' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '{{- end }}' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '# NoSQL Table Names' + '\n')
                
                for key, value in self.nosql.tables.items():
                    f.write('  ' + '  ' + '  ' + '  ' + f'- name: {key.upper()}' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-storage-tables' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + f'key: {value["name"]}' + '\n')
            
            if self.uses_cache:
                f.write('  ' + '  ' + '  ' + '  ' + '# Caching Server Variables' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: CACHE_HOSTNAME' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Relese.name }}-cache-configmap' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: hostname' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: CACHE_PORT' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-cache-configmap' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: port' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: CACHE_PASSWORD' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-cache-credentials' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: password' + '\n')
            
            f.write('  ' + '  ' + '  ' + '  ' + '# Third-Party Integrations' + '\n')
            for third_party in self.third_party_services:
                f.write('  ' + '  ' + '  ' + '  ' + '{{- if .Values.thirdParty.' + third_party.name + '.enabled }}' + '\n')
                
                for var in third_party.vars:
                    f.write('  ' + '  ' + '  ' + '  ' + '- name: ' + third_party.name.upper() + '_' + var.upper() + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n')
                    f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
                    f.write('  ' + '  '  '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-' + third_party.name + '-secret' + '\n')
                    f.write('  ' + '  '  '  ' + '  ' + '  ' + '  ' + '  ' + f'key: {var.replace("_", "-")}' + '\n')
                
                f.write('  ' + '  ' + '  ' + '  ' + '{{- end }}' + '\n')
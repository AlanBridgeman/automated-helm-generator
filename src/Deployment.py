from .Template import Template
from .NoSQL import NoSQL
from .ThirdPartyService import ThirdPartyService

class Deployment (Template):
    def __init__(self, image_repository: str, image_tag: str = 'v1.0.0', image_pull_policy: str = 'IfNotPresent', replica_count: int = 1, port: int = 8080, env: str = 'production', uses_oauth: bool = True, uses_db: bool = False, uses_secrets_vault: bool = False, nosql: NoSQL | None = None, uses_cache: bool = False, third_party_services: list[ThirdPartyService] = [], **extra_env_vars: dict[str, str | dict[str, str]]):
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
            uses_secrets_vault (bool, Optional): Whether or not a secrets vault is to be used. Determines if secrets vault related environment variables need to be set on the Deployment. Default False
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
        self.uses_secrets_vault = uses_secrets_vault
        self.nosql = nosql
        self.uses_cache = uses_cache
        self.third_party_services = third_party_services
        self.extra_env_vars = extra_env_vars
    
    def write_extra_env_vars_secret_file(self, env_var_details: dict[str, str]):
        """Writes a Secret file for the extra environment variable.
        
        Args:
            env_var_details (dict[str, str]): The details of the environment variable.
        """

        filename = env_var_details['name']
        if filename.startswith('{{ .Release.Name }}'):
            filename = filename.replace('{{ .Release.Name }}-', '')
                    
        camel_case_name = filename.split('-')[0]
        for token in filename.split('-'):
            if token != camel_case_name:
                camel_case_name += token.capitalize()

        with open(f'templates/{filename}-secret.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + f'name: {env_var_details["name"]}' + '\n')
            f.write('type: Opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + f'{env_var_details["key"]}: ' + '{{ .Values.' + camel_case_name + ' | b64enc }}' + '\n')
    
    def write_extra_env_vars_configmap_file(self, env_var_details: dict[str, str]):
        """Writes a ConfigMap file for the extra environment variable.
        
        Args:
            env_var_details (dict[str, str]): The details of the environment variable.
        """

        filename = env_var_details['name']
        if filename.startswith('{{ .Release.Name }}'):
            filename = filename.replace('{{ .Release.Name }}-', '')
            
            camel_case_name = filename.split('-')[0]
            for token in filename.split('-'):
                if token != camel_case_name:
                    camel_case_name += token.capitalize()

            with open(f'templates/{filename}-configmap.yaml', 'w') as f:
                f.write('apiVersion: v1' + '\n')
                f.write('kind: ConfigMap' + '\n')
                f.write('metadata:' + '\n')
                f.write('  ' + f'name: {env_var_details["name"]}' + '\n')
                f.write('data:' + '\n')
                f.write('  ' + f'{env_var_details["key"]}: {{ .Values.{camel_case_name} }}' + '\n')
    
    def write_extra_env_vars_files(self):
        """Writes any needed secret or configmap files for the extra environment variables."""
        
        for value in self.extra_env_vars.values():
            # We only need to crate a secret or configmap file if the value is a dictionary
            # Because if it's a string we'll just use it as the value of the environment variable
            if isinstance(value, dict):
                if value['type'] == 'Secret':
                    self.write_extra_env_vars_secret_file(value)
                elif value['type'] == 'ConfigMap':
                    self.write_extra_env_vars_configmap_file(value)

    def create_extra_env_vars_deployment_env_vars(self) -> str:
        """Creates the extra environment variables actual variables for the Deployment."""
        
        output = ''

        for key, value in self.extra_env_vars.items():
            # Check if the value is a dictionary or a string
            if isinstance(value, dict):
                output += '  ' + '  ' + '  ' + '  ' + f'- name: {key.upper()}' + '\n'
                output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
                
                if value['type'] == 'Secret':
                    output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
                elif value['type'] == 'ConfigMap':
                    output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
                
                output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: ' + value['name'] + '\n'
                output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: ' + value['key'] + '\n'
            else:
                # Because the value is a string just use the value literally
                output += '  ' + '  ' + '  ' + '  ' + f'- name: {key.upper()}' + '\n'
                output += '  ' + '  ' + '  ' + '  ' + '  ' + f'value: {value}' + '\n'
        
        return output
    
    def create_oauth_deployment_env_vars(self) -> str:
        """Creates the OAuth related environment variables for the Deployment."""

        output = ''

        output += '  ' + '  ' + '  ' + '  ' + '# OAuth Implementation Stuff' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: BASE_APP_URL' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: base-app-url' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: APP_ABBRV' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: app-abbreviation' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: APP_NAME' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: app-name' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: SERVICE_NAME' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: service-name' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: DEV_PORT' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: dev-port' + '\n'

        return output
    
    def create_db_deployment_env_vars(self) -> str:
        """Creates the database related environment variables for the Deployment."""

        output = ''

        output += '  ' + '  ' + '  ' + '  ' + '# Database credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: DB_HOST' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-host' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: DB_NAME' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-name' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: DB_PASSWORD' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-password' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: password' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: DB_PORT' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-port' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: DB_USER' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-user' + '\n'

        return output
    
    def create_nosql_deployment_env_vars(self) -> str:
        """Creates the NoSQL related environment variables for the Deployment."""

        output = ''

        output += '  ' + '  ' + '  ' + '  ' + '# NoSQL Credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- if eq .Values.nosql.type "mongodb" }}' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: STORAGE_ACCOUNT_CONNECTION_STRING' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-mongo-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: connection-string' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- else if eq .Values.nosql.type "azure" }}' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: STORAGE_ACCOUNT_KEY' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-azure-tables-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: key' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: STORAGE_ACCOUNT_NAME' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-azure-tables-config' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: name' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- end }}' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '# NoSQL Table Names' + '\n'
        
        for key, value in self.nosql.tables.items():
            output += '  ' + '  ' + '  ' + '  ' + f'- name: {key.upper()}' + '\n'
            output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
            output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
            output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-storage-tables' + '\n'
            output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + f'key: {value["name"]}' + '\n'
        
        return output

    def create_secret_vault_deployment_env_vars(self) -> str:
        """Creates the secret vault related environment variables for the Deployment."""

        output = ''
        
        output += '  ' + '  ' + '  ' + '  ' + '# -- Secrets Vault (Hashicorp Vault OR Azure Key Vault) --' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- if .Values.vault.enabled }}' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- if eq .Values.vault.type "azure" }}' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: KEYVAULT_CLIENT_ID' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: client-id' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: KEYVAULT_CLIENT_SECRET' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: client-secret' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: KEYVAULT_NAME' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: name' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: KEYVAULT_TENANT_ID' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: tenant-id' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- else if eq .Values.vault.type "hashicorp" }}' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: VAULT_NAME' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: vault-name' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: VAULT_PORT' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: vault-port' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- end }}' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '{{- end }}' + '\n'

        return output

    def create_cache_deployment_env_vars(self) -> str:
        """Creates the cache related environment variables for the Deployment."""

        output = ''

        output += '  ' + '  ' + '  ' + '  ' + '# Caching Server Variables' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: CACHE_HOSTNAME' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Relese.name }}-cache-configmap' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: hostname' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: CACHE_PORT' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-cache-configmap' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: port' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '- name: CACHE_PASSWORD' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-cache-credentials' + '\n'
        output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'key: password' + '\n'

        return output
    
    def create_third_party_services_deployment_env_vars(self) -> str:
        """Creates the third party services related environment variables for the Deployment."""
        
        output = ''

        output += '  ' + '  ' + '  ' + '  ' + '# Third-Party Integrations' + '\n'
        for third_party in self.third_party_services:
            output += '  ' + '  ' + '  ' + '  ' + '{{- if .Values.thirdParty.' + third_party.name + '.enabled }}' + '\n'
                
            for var in third_party.vars:
                output += '  ' + '  ' + '  ' + '  ' + '- name: ' + third_party.name.upper() + '_' + var.upper() + '\n'
                output += '  ' + '  ' + '  ' + '  ' + '  ' + 'valueFrom:' + '\n'
                output += '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'secretKeyRef:' + '\n'
                output += '  ' + '  '  '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-' + third_party.name + '-secret' + '\n'
                output += '  ' + '  '  '  ' + '  ' + '  ' + '  ' + '  ' + f'key: {var.replace("_", "-")}' + '\n'
                
            output += '  ' + '  ' + '  ' + '  ' + '{{- end }}' + '\n'
        
        return output
    
    def write_deployment_file(self):
        """Writes the Deployment file for the app."""

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
            
            # Add extra environment variables
            f.write(self.create_extra_env_vars_deployment_env_vars())

            if self.uses_oauth:
                f.write(self.create_oauth_deployment_env_vars())
            
            if self.uses_db:
                f.write(self.create_db_deployment_env_vars())
            
            if self.nosql is not None:
                f.write(self.create_nosql_deployment_env_vars())
            
            if self.uses_secrets_vault:
                f.write(self.create_secret_vault_deployment_env_vars()) 

            if self.uses_cache:
                f.write(self.create_cache_deployment_env_vars())
            
            if len(self.third_party_services) > 0:
                f.write(self.create_third_party_services_deployment_env_vars())
            
            # Because of the way we implement Hashicorp Vault we need to mount the role_vars shared volume 
            # This is because the Vault container populates this shared volume with the app credentials. 
            # It's done this way because we don't know the credentials needed to access the vault at start time (because their generated by the Vault container)
            # So, we need a mechanism to get these credentials in relatively real-time once they've been generated
            if self.uses_secrets_vault:
                f.write('  ' + '  ' + '  ' + '  ' + 'volumeMounts:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '- name: role-vars' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'mountPath: /role_vars' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'readOnly: true' + '\n')
                f.write('  ' + '  ' + '  ' + 'volumes:' + '\n')
                f.write('  ' + '  ' + '  ' + '- name: role-vars' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + 'persistentVolumeClaim:' + '\n')
                f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'claimName: {{ .Release.Name }}-vault-role-vars' + '\n')
    
    def write(self):
        """Writes files related to the Deployment of the app."""
        
        # Create any needed secrets or configmaps for the extra environment variables
        self.write_extra_env_vars_files()

        # Create the Deployment file
        self.write_deployment_file()
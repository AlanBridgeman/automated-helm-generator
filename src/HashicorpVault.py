from .SecretsVault import SecretsVault

class HashicorpVault(SecretsVault):
    def __init__(self, create: bool = True, image: dict[str, str] | None = None, hostname: str | None = None, port: int = 8200, storage_class: str | None = None, storage_size: str = '512Mi'):
        super().__init__('hashicorp')

        self.create = create
        self.image = image
        self.hostname = hostname
        self.port = port
        self.storage_class = storage_class
        self.storage_size = storage_size
    
    def write_ingress(self):
        with open('templates/vault-ingress.yaml', 'w') as f:
            f.write('{{- if .Values.vault.create.ingress.enabled -}}' + '\n')
            f.write('apiVersion: networking.k8s.io/v1' + '\n')
            f.write('kind: Ingress' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-vault-ingress' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}-vault' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'ingressClassName: nginx' + '\n')
            f.write('  ' + 'rules:' + '\n')
            f.write('  ' + '  ' + '- host: {{ .Values.vault.create.ingress.host }}' + '\n')
            f.write('  ' + '  ' + '  ' + 'http:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'paths:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- path: /' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'pathType: Prefix' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'backend:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'service:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}-vault' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'port:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'number: 80' + '\n')
            f.write('{{- end -}}')
    
    def write_service(self):
        with open('templates/vault-service.yaml', 'w') as f:
            f.write('{{- if .Values.vault.create.enabled -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Service' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-vault' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}-vault' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'selector:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}-vault' + '\n')
            f.write('  ' + 'ports:' + '\n')
            f.write('  ' + '  ' + '- protocol: TCP' + '\n')
            f.write('  ' + '  ' + '  ' + 'port: 80' + '\n')
            f.write('  ' + '  ' + '  ' + 'targetPort: 8200' + '\n') 
            f.write('{{- end -}}')
    
    def write_role_vars_persistent_volume_claim(self):
        with open('templates/vault-role-vars-persistent-volume-claim.yaml', 'w') as f:
            f.write('{{- if .Values.vault.create.enabled -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: PersistentVolumeClaim' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-vault-role-vars' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}-vault' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'storageClassName: {{ .Values.vault.create.storage.storageClass }}' + '\n')
            f.write('  ' + 'accessModes:' + '\n')
            f.write('  ' + '  ' + '- ReadWriteMany' + '\n')
            f.write('  ' + 'resources:' + '\n')
            f.write('  ' + '  ' + 'requests:' + '\n')
            f.write('  ' + '  ' + '  ' + 'storage: {{ .Values.vault.create.storage.size }}' + '\n')
            f.write('{{- end -}}')
    
    def write_deployment(self):
        with open('templates/vault-deployment.yaml', 'w') as f:
            f.write('{{- if and (.Values.vault.create.enabled) (eq .Values.vault.type "hashicorp") -}}' + '\n')
            f.write('apiVersion: apps/v1' + '\n')
            f.write('kind: Deployment' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-vault' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}-vault' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'replicas: 1' + '\n')
            f.write('  ' + 'selector:' + '\n')
            f.write('  ' + '  ' + 'matchLabels:' + '\n')
            f.write('  ' + '  ' + '  ' + 'app: {{ .Release.Name }}-vault' + '\n')
            f.write('  ' + 'template:' + '\n')
            f.write('  ' + '  ' + 'metadata:' + '\n')
            f.write('  ' + '  ' + '  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'app: {{ .Release.Name }}-vault' + '\n')
            f.write('  ' + '  ' + 'spec:' + '\n')
            f.write('  ' + '  ' + '  ' + 'containers:' + '\n')
            f.write('  ' + '  ' + '  ' + '- name: {{ .Release.Name }}-vault' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'image: {{ .Values.vault.create.image.repository }}:{{ .Values.vault.create.image.tag }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'ports:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- containerPort: 8200' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- containerPort: 8201' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'env:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: VAULT_ADDR' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'value: http://0.0.0.0:8200' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: ROLE_ID_SECRET_NAME' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'value: VAULT_ROLE_ID' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: SECRET_ID_SECRET_NAME' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'value: VAULT_SECRET_ID' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'volumeMounts:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: vault-data' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'mountPath: /vault/data' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: vault-log' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'mountPath: /vault/logs' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: vault-creds' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'mountPath: /vault/creds' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: vault-role-vars' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'mountPath: /role_vars' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'capAdd:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- IPC_LOCK' + '\n')
            f.write('  ' + '  ' + '  ' + 'volumes:' + '\n')
            f.write('  ' + '  ' + '  ' + '- name: vault-data' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'emptyDir: {}' + '\n')
            f.write('  ' + '  ' + '  ' + '- name: vault-log' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'emptyDir: {}' + '\n')
            f.write('  ' + '  ' + '  ' + '- name: vault-creds' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'emptyDir: {}' + '\n')
            f.write('  ' + '  ' + '  ' + '- name: vault-role-vars' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'persistentVolumeClaim:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'claimName: {{ .Release.Name }}-vault-role-vars' + '\n')
            f.write('{{- end -}}')
    
    def write_secret(self):
        with open('templates/vault-hashicorp-secret.yaml', 'w') as f:
            f.write('{{- if and (.Values.vault.enabled) (eq .Values.vault.type "hashicorp") -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n')
            f.write('type: opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + '{{- if .Values.vault.create.enabled }}' + '\n')
            f.write('  ' + '# Because we create the Hashicorp Vault instance as part of the Helm chart, ' + '\n')
            f.write('  ' + '# we can use the name of the created resource (utilizing k8s built-in container connections)' + '\n')
            f.write('  ' + '# to connect to the Vault instance without having to hard-code the Vault name.' + '\n')
            f.write('  ' + 'vault-name: {{ printf "%s-vault" .Release.Name | b64enc }}' + '\n')
            f.write('  ' + '# Because we create the Hashicorp Vault instance as part of the Helm chart,' + '\n')
            f.write('  ' + '# We know the port that the Vault instance is running on.' + '\n')
            f.write('  ' + 'vault-port: {{ printf "%d" 80 | b64enc }}' + '\n')
            f.write('  ' + '{{- else }}' + '\n')
            f.write('  ' + '# Because the Vault wasn\'t created as part of the Helm chart,' + '\n')
            f.write('  ' + '# we need the deployer to specify the name of the Vault instance to connect to.' + '\n')
            f.write('  ' + 'vault-name: {{ .Values.vault.vaultName | b64enc }}' + '\n')
            f.write('  ' + '# Because the Vault wasn\'t created as part of the Helm chart,' + '\n')
            f.write('  ' + '# we need the deployer to specify the port that the Vault instance is running on.' + '\n')
            f.write('  ' + 'vault-port: {{ .Values.passVault.vaultPort | b64enc }}' + '\n')
            f.write('  ' + '{{- end }}' + '\n')
            f.write('{{- end -}}')
    
    def write(self):
        self.write_ingress()
        self.write_service()
        self.write_role_vars_persistent_volume_claim()
        self.write_deployment()
        self.write_secret()
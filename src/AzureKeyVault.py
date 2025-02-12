from .SecretsVault import SecretsVault

class AzureKeyVault(SecretsVault):
    def __init__(self, name: str, client_id: str, client_secret: str, tenant_id: str):
        super().__init__('azure')

        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
    
    def write(self):
        with open('templates/vault-keyvault-secret.yaml', 'w') as f:
            f.write('{{- if and (.Values.vault.enabled) (eq .Values.vault.type "azure") -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-vault-secret' + '\n')
            f.write('type: opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'client-id: {{ .Values.vault.clientId | b64enc }}' + '\n')
            f.write('  ' + 'client-secret: {{ .Values.vault.clientSecret | b64enc }}' + '\n')
            f.write('  ' + 'name: {{ .Values.vault.vaultName | b64enc }}' + '\n')
            f.write('  ' + 'tenant-id: {{ .Values.vault.tenantId | b64enc }}' + '\n')
            f.write('{{- end -}}')
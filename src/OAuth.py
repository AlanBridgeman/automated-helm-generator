from .Template import Template

class OAuth (Template):
    def __init__(self, base_app_url: str, app_abbreviation: str, app_name: str, service_name: str, dev_port: str, client_id: str, client_secret: str):
        """A class for creating a/some template(s) related to OAuth implementation."""

        self.base_app_url = base_app_url
        self.app_abbreviation = app_abbreviation
        self.app_name = app_name
        self.service_name = service_name
        self.dev_port = dev_port
        self.client_id = client_id
        self.client_secret = client_secret
    
    def write(self):
        with open('templates/oauth-credentials-config-map.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: ConfigMap' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-oauth-credentials' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'base-app-url: {{ .Values.oauth.baseAppUrl }}' + '\n')
            f.write('  ' + 'app-abbreviation: {{ .Values.oauth.appAbbreviation }}' + '\n')
            f.write('  ' + 'app-name: {{ .Values.oauth.appName }}' + '\n')
            f.write('  ' + 'service-name: {{ .Values.oauth.serviceName }}' + '\n')
            f.write('  ' + 'dev-port: {{ .Values.oauth.devPort | quote }}' + '\n')
            f.write('  ' + 'client-id: {{ .Values.oauth.clientId | quote }}' + '\n')
        
        with open('templates/oauth-client-secret.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-oauth-client-secret' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('type: Opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'client-secret: {{ .Values.oauth.clientSecret | b64enc }}' + '\n')
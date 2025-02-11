from .Template import Template

class Ingress (Template):
    def __init__(self, hostname: str):
        """A class for creating a/some template(s) related to the Ingress for the app.
        
        Args:
            hostname (str): The hostname that the Ingress will be accessed on.
        """
        
        super().__init__()

        self.hostname = hostname
    
    def write(self):
        """Write the Ingress template to a file."""
        
        with open(f'templates/ingress.yaml', 'w') as f:
            f.write('{{- if .Values.ingress.enabled -}}' + '\n')
            f.write('apiVersion: networking.k8s.io/v1' + '\n')
            f.write('kind: Ingress' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}' + '\n')
            f.write('  ' + 'annotations:' + '\n')
            f.write('  ' + '  ' + 'nginx.ingress.kubernetes.io/rewrite-target: /' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'rules:' + '\n')
            f.write('  ' + '- host: {{ .Values.ingress.host }}' + '\n')
            f.write('  ' + '  ' + 'http:' + '\n')
            f.write('  ' + '  ' + '  ' + 'paths:' + '\n')
            f.write('  ' + '  ' + '  ' + '- path: /' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'pathType: Prefix' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + 'backend:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'service:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'name: {{ .Release.Name }}' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'port:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + '  ' + '  ' + 'number: 80' + '\n')
            f.write('  ' + 'ingressClassName: {{ .Values.ingress.class }}' + '\n')
            f.write('{{- end -}}')
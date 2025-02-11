from .Template import Template

class Service (Template):
    def __init__(self):
        """A class for creating a/some template(s) related to the Service for the app."""
        
        super().__init__()
    
    def write(self):
        """Write the Service template to a file."""
        
        with open(f'templates/service.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Service' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'selector:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('  ' + 'ports:' + '\n')
            f.write('  ' + '  ' + '- protocol: TCP' + '\n')
            f.write('  ' + '  ' + '  ' + 'port: 80' + '\n')
            f.write('  ' + '  ' + '  ' + 'targetPort: {{ .Values.container.port }}' + '\n')
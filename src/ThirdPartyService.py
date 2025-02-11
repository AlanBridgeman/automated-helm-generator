from .Template import Template

class ThirdPartyService (Template):
    def __init__(self, name: str, enabled: bool, **vars: str):
        super().__init__()

        self.name = name
        self.enabled = enabled
        self.vars = vars

    def write(self):
        with open(f'templates/{self.name}-secret.yaml', 'w') as f:
            f.write('{{- if .Values.thirdParty.' + self.name + '.enabled -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-' + self.name + '-secret' + '\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('type: Opaque' + '\n')
            f.write('data:' + '\n')
            for key, value in self.vars.items():
                snake_case_name = key.split('_')[0]
                for token in key.split('_'):
                    if token != snake_case_name:
                        snake_case_name += token.capitalize()
                
                f.write('  ' + key.replace('_', '-') + ': {{ .Values.thirdParty.' + self.name + '.' + snake_case_name + ' | b64enc }}' + '\n')
            
            f.write('{{- end -}}' + '\n')
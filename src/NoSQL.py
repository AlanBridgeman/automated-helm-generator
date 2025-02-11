from .Template import Template

class NoSQL (Template):
    def __init__(self, type: str, db_name: str, tables: dict[str, dict[str, str]], create: bool = True):
        super().__init__()

        self.type = type
        self.db_name = db_name
        self.tables = tables
        self.create = create
    
    def write(self):
        with open('templates/storage-tables-config-map.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: ConfigMap' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-storage-tables' +'\n')
            f.write('  ' + 'labels:' + '\n')
            f.write('  ' + '  ' + 'app: {{ .Release.Name }}' + '\n')
            f.write('data:' + '\n')

            # Loop over tables dictionary and get the values
            for value in self.tables.values():
                snake_case_name = value['name'].split('-')[0]
                for token in value['name'].split('-'):
                    if token != snake_case_name:
                        snake_case_name += token.capitalize()
                
                f.write('  ' + value['name'] + ': {{ .Values.tables.' + snake_case_name + ' }}' + '\n')
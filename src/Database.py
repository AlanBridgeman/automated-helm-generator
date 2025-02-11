from .Template import Template

class Database (Template):
    def __init__(self, name: str, host: str, user: str, password: str, create: bool = True, port: int = 5432, instance_id: str = ''):
        """A class for creating a/some template(s) related to a database.
        
        Args:
            name (str): The name of the database to be used.
            host (str): The host that the database is located on.
            user (str): The user that is used to access the database.
            password (str): The password that is used to access the database.
            create (bool, Optional): If set to `True`, the database will be created as part of the deployment. This uses the [`postgres-controller` CRD](https://github.com/AlanBridgeman/postgres-controller) to create the database. Default True
            port (int, Optional): The port that the database listens on. Default 5432
            instance_id (str, Optional): Allows for distinguishing between multiple database instances/servers. Default ''
        """

        # The type of the relational database that is used.
        # 
        # The following table lists the possible values for this field:
        # 
        # | Value      | Description                                |
        # | ---------- | ------------------------------------------ |
        # | `postgres` | Uses PostgreSQL as the relational database |
        # 
        # Note, for use of `postgres`, it uses a [`postgres-controller` CRD](https://github.com/AlanBridgeman/postgres-controller) to create the database
        # 
        self.type = 'postgres'
        
        # If set to `true`, the database will be created as part of the deployment
        # This uses the [`postgres-controller` CRD](https://github.com/AlanBridgeman/postgres-controller) to create the database
        self.create = create
        
        # The host that the database is located on
        self.host = host
        
        # The name of the database to be used
        self.name = name
        
        # The user that is used to access the database
        self.user = user
        
        # The password that is used to access the database
        self.password = password
        
        # The port that the database listens on
        self.port = port

        # Allows for distinguishing between multiple database instances/servers
        self.instance_id = instance_id
    
    def write(self):
        # Config Map file for use within the Postgres Controller namespace
        # This is required by the operator to function properly
        with open('templates/db-credentials-config-map-postgres-controller.yaml', 'w') as f:
            f.write('{{- if and (eq .Values.database.type "postgres") (.Values.database.create) -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: ConfigMap' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n')
            f.write('  ' + 'namespace: postgres-controller' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'db-host: {{ .Values.database.host }}' + '\n')
            f.write('  ' + 'db-name: {{ .Values.database.name }}' + '\n')
            f.write('  ' + 'db-user: {{ .Values.database.user }}' + '\n')
            f.write('  ' + '{{- if .Values.database.port }}' + '\n')
            f.write('  ' + 'db-port: {{ .Values.database.port | quote }}' + '\n')
            f.write('  ' + '{{- else }}' + '\n')
            f.write('  ' + 'db-port: "5432"' + '\n')
            f.write('  ' + '{{- end }}' + '\n')
            f.write('{{- end -}}' + '\n')
        
        # Config Map file in the same namespace as the app
        with open('templates/db-credentials-config-map.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: ConfigMap' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-db-credentials' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'db-host: {{ .Values.database.host }}' + '\n')
            f.write('  ' + 'db-name: {{ .Values.database.name }}' + '\n')
            f.write('  ' + 'db-user: {{ .Values.database.user }}' + '\n')
            f.write('  ' + '{{- if .Values.database.port }}' + '\n')
            f.write('  ' + 'db-port: {{ .Values.database.port | quote }}' + '\n')
            f.write('  ' + '{{- else }}' + '\n')
            f.write('  ' + 'db-port: "5432"' + '\n')
            f.write('  ' + '{{- end }}' + '\n')
        
        # Secret file for the password to access the database for use within the Postgres Controller namespace
        # This is required by the operator to function properly
        with open('templates/db-password-secret-postgres-controller.yaml', 'w') as f:
            f.write('{{- if and (eq .Values.database.type "postgres") (.Values.database.create) -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-db-password' + '\n')
            f.write('  ' + 'namespace: postgres-controller' + '\n')
            f.write('type: Opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'password: {{ .Values.database.password | b64enc }}' + '\n')
            f.write('{{- end -}}' + '\n')
        
        # Secret file for the password to access the database in the same namespace as the app
        with open('templates/db-password-secret.yaml', 'w') as f:
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-db-password' + '\n')
            f.write('type: Opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'password: {{ .Values.database.password | b64enc }}' + '\n')

        # Custom Resource Definition (CRD) file to create the database using the operator 
        with open('templates/database.yaml', 'w') as f:
            f.write('{{- if and (eq .Values.database.type "postgres") (.Values.database.create) -}}' + '\n')
            f.write('apiVersion: postgresql.org/v1' + '\n')
            f.write('kind: PostgresDatabase' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-db' + '\n')
            f.write('  ' + 'namespace: {{ .Release.Namespace }}' + '\n')
            f.write('spec:' + '\n')
            f.write('  ' + 'dbName:' + '\n')
            f.write('  ' + '  ' + 'envFrom:' + '\n')
            f.write('  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: {{ .Release.Name }}-db-credentials' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'namespace: postgres-controller' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-name' + '\n')
            f.write('  ' + 'dbRoleName:' + '\n')
            f.write('  ' + '  ' + 'envFrom:' + '\n')
            f.write('  ' + '  ' + '  ' + 'configMapKeyRef:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: {{ .Release.Name }}-db-credentials' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'namespace: postgres-controller' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'key: db-user' + '\n')
            f.write('  ' + 'dbRolePassword:' + '\n')
            f.write('  ' + '  ' + 'envFrom:' + '\n')
            f.write('  ' + '  ' + '  ' + 'secretKeyRef:' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '- name: {{ .Release.Name }}-db-password' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'namespace: postgres-controller' + '\n')
            f.write('  ' + '  ' + '  ' + '  ' + '  ' + 'key: password' + '\n')
            f.write('{{- if .Values.database.instance_id }}' + '\n')
            f.write('  ' + 'dbInstanceId: {{ .Values.database.instance_id }}' + '\n')
            f.write('{{- end }}' + '\n')
            f.write('{{- end -}}' + '\n')
from .NoSQL import NoSQL

class AzureTableStorage (NoSQL):
    def __init__(self, db_name: str, key: str, tables: dict[str, dict[str, str]]):
        """Use of Azure Table Storage (Azure Storage Account) as a NoSQL storage system
        
        Args:
            db_name (str): The name of the Azure Storage Account to connect to
            key (str): The key to use to connect to the Azure Storage Account
            tables (dict[str, dict[str, str]]): A dictionary of table names and their details
        """
        
        # Call the parent class constructor
        # Note, the following:
        # - The type is set to 'azure' because we are using Azure Table Storage
        # - The create parameter is set to False because an Azure Storage Account can't be created/provisioned as part of a Helm deployment
        super().__init__('azure', db_name, tables, False)
        
        self.key = key
    
    def write_config_map(self, filename: str = 'azure-tables-configmap.yaml'):
        """Writes the configmap file for the Azure Table Storage

        This configmap contains non-sensitive information about the Azure Table Storage.
        Such as the name of the Azure Storage Account to connect to.
        
        Args:
            filename (str, optional): The name of the file to write to. Defaults to 'azure-tables-configmap.yaml'.
        """

        with open(f'templates/{filename}', 'w') as f:
            f.write('{{- if eq .Values.nosql.type "azure" -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: ConfigMap' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-azure-tables-config' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'name: {{ .Values.nosql.name }}' + '\n')
            f.write('{{- end -}}' + '\n')
    
    def write_secret(self, filename: str = 'azure-tables-credentials-secret.yaml'):
        """Writes the secret file for the Azure Table Storage
        
        This secret contains sensitive information about the Azure Table Storage.
        Such as the key to use to connect to the Azure Storage Account.

        Args:
            filename (str, optional): The name of the file to write to. Defaults to 'azure-tables-credentials-secret.yaml'.
        """

        with open(f'templates/{filename}', 'w') as f:
            f.write('{{- if eq .Values.nosql.type "azure" -}}' + '\n')
            f.write('apiVersion: v1' + '\n')
            f.write('kind: Secret' + '\n')
            f.write('metadata:' + '\n')
            f.write('  ' + 'name: {{ .Release.Name }}-azure-tables-credentials' + '\n')
            f.write('type: Opaque' + '\n')
            f.write('data:' + '\n')
            f.write('  ' + 'key: {{ .Values.nosql.key | b64enc }}' + '\n')
            f.write('{{- end -}}' + '\n')
    
    def write(self):
        """Writes the needed template files for the Azure Table Storage"""
        
        self.write_config_map()
        self.write_secret()
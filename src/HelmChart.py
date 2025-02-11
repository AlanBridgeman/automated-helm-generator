import os, subprocess

from .Template import Template
from .Ingress import Ingress
from .Database import Database
from .NoSQL import NoSQL
from .MongoDB import MongoDB
from .Redis import Redis
from .OAuth import OAuth
from .ThirdPartyService import ThirdPartyService
from .Deployment import Deployment

class HelmChart:
    def __init__(self, chartName: str, chartDescription: str, maintainers: list[dict[str, str]], chartHomepage: str, sources: list[str], appVersion: str = '1.0.0', chartVersion: str = '1.0.0', apiVersion: str = 'v1', *templates: Template):
        """A class for creating a Helm chart.
        
        Args:
            chartName (str): The name of the Helm chart.
            chartDescription (str): A description of the Helm chart.
            maintainers (list[dict[str, str]]): The maintainers of the Helm chart.
            chartHomepage (str): The URL of the Helm chart's home page
            sources (list[str]): The sources of the Helm chart.
            appVersion (str, Optional): The version of the application that the Helm chart is deploying. Default '1.0.0'
            chartVersion (str, Optional): The version of the Helm chart. Default '1.0.0'
            apiVersion (str, Optional): The API version of the Helm chart itself. Default 'v1'
            Templates (Template, Optional): The templates for the Helm chart. Default None
        """
        
        self.chartName = chartName
        self.chartDescription = chartDescription
        self.maintainers = maintainers
        self.chartHomepage = chartHomepage
        self.sources = sources
        self.appVersion = appVersion
        self.chartVersion = chartVersion
        self.apiVersion = apiVersion
        self.templates = templates
    
    def create_templates_folder(self):
        """Create the templates folder for the Helm chart."""

        os.mkdir('templates')

        for template in self.templates:
            template.write()

    def write_yaml(self):
        """Write the Chart.yaml file for the Helm chart."""

        with open('Chart.yaml', 'w') as f:
            f.write(f'apiVersion: {self.apiVersion}' + '\n')
            f.write(f'appVersion: "{self.appVersion}"' + '\n')
            f.write(f'description: {self.chartDescription}' + '\n')
            f.write(f'home: {self.chartHomepage}' + '\n')
            f.write('maintainers:' + '\n')
            for maintainer in self.maintainers:
                f.write('  ' + f'- email: {maintainer["email"]}' + '\n')
                f.write('  ' + '  ' + f'name: {maintainer["name"]}' + '\n')
            f.write(f'name: {self.chartName}' + '\n')
            f.write('sources:' + '\n')
            for source in self.sources:
                f.write(f'- {source}' + '\n')
            f.write(f'version: "{self.chartVersion}"' + '\n')
    
    def write_values_yaml(self):
        """Write the values.yaml file for the Helm chart."""

        # Get the Deployment and Ingress templates from the templates provided
        deployment_template = next(template for template in self.templates if isinstance(template, Deployment))
        ingress_template = next(template for template in self.templates if isinstance(template, Ingress))

        with open('values.yaml', 'w') as f:
            f.write('# The number of instances (replicas) of the app to run' + '\n')
            f.write(f'replicaCount: {deployment_template.replica_count}' + '\n')
            f.write('\n')
            
            f.write('image:' + '\n')
            f.write('  ' + '# The repository of the image to use for the app' + '\n')
            f.write('  ' + '# Should be in the format `<Image Repository (Ex. containers.example.com)>/<Image Name (Ex. app)>`' + '\n')
            f.write('  ' + f'repository: "{deployment_template.image_repository}"' + '\n')
            f.write('  ' + '# The specific image tag to use. It\'s recommended to use some kind of versioning tag scheme as it makes updating the container without having to fully redeploy easier.' + '\n')
            f.write('  ' + '# Ex. v1.0.0' + '\n')
            f.write('  ' + f'tag: "{deployment_template.image_tag}"' + '\n')
            f.write('  ' + '# How often the image should be pulled. The possible values are "Always", "Never", and "IfNotPresent"' + '\n')
            f.write('  ' + '# It\'s recommended for production to use "IfNotPresent" to avoid pulling the image every time the pod starts' + '\n')
            f.write('  ' + '# Though, for development, "Always" is recommended to ensure the latest changes are being tested' + '\n')
            f.write('  ' + f'pullPolicy: "{deployment_template.image_pull_policy}"' + '\n')
            f.write('\n')
            
            f.write('container:' + '\n')
            f.write('  ' + '# The port that the container listens on (Ex. 8080)' + '\n')
            f.write('  ' + f'port: {deployment_template.port}' + '\n')
            f.write('  ' + '\n')
            f.write('  ' + '# The environment that the container is running in (Ex. development, production, etc...)' + '\n')
            f.write('  ' + '# This is used for the NODE_ENV environment variable' + '\n')
            f.write('  ' + f'env: "{deployment_template.env}"' + '\n')
            f.write('\n')
            
            f.write('ingress:' + '\n')
            f.write('  ' + '# We want an ingress resource if we are deploying to a cluster that has a ingress controller/load balancer' + '\n')
            f.write('  ' + '# This includes most public cloud providers like EKS, GKE, and AKS' + '\n')
            f.write('  ' + 'enabled: true' + '\n')
            f.write('  ' + '# The DNS Name (Ex. app.example.com) where the app will be accessible' + '\n')
            f.write('  ' + f'host: "{ingress_template.hostname}"' + '\n')
            f.write('  ' + '# The class of the ingress controller that is being used (defaulted here to an NGINX ingress controller as it\'s popular for Kubernetes clusters)' + '\n')
            f.write('  ' + 'class: nginx' + '\n')
            f.write('\n')
            
            for value in deployment_template.extra_env_vars.values():
                if isinstance(value, dict):
                    # If a description is provided for the environment variable than we want to include it as a comment above the value in the `values.yaml` file.
                    if 'description' in value:
                        f.write(f'# {value["description"]}' + '\n')
                    
                    var_name = value["name"].replace('{{ .Release.Name }}-', '')
                    snake_case_name = var_name.split('-')[0]
                    for token in var_name.split('-'):
                        if token != snake_case_name:
                            snake_case_name += token.capitalize()
                    
                    f.write(f'{snake_case_name}: "{value["value"]}"' + '\n')
            #f.write('privateRegistryToken: "<Private Registry Token>"' + '\n')
            f.write('\n')

            # If a OAuth template is included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, OAuth) for template in self.templates):
                # Get the OAuth template from the templates provided
                oauth_template = next(template for template in self.templates if isinstance(template, OAuth))

                f.write('# Configuration for using OAuth within the app' + '\n')
                f.write('oauth:' + '\n')
                f.write('  ' + f'baseAppUrl: "{oauth_template.base_app_url}"' + '\n')
                f.write('  ' + f'appAbbreviation: "{oauth_template.app_abbreviation}"' + '\n')
                f.write('  ' + f'appName: "{oauth_template.app_name}"' + '\n')
                f.write('  ' + f'serviceName: "{oauth_template.service_name}"' + '\n')
                f.write('  ' + f'devPort: "{oauth_template.dev_port}"' + '\n')
                f.write('  ' + f'clientId: "{oauth_template.client_id}"' + '\n')
                f.write('  ' + f'clientSecret: "{oauth_template.client_secret}"' + '\n')
                f.write('\n')
            
            # If a Database template is included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, Database) for template in self.templates):
                # Get the Database template from the templates provided
                database_template = next(template for template in self.templates if isinstance(template, Database))

                f.write('# Configuration for the relational database' + '\n')
                f.write('database:' + '\n')
                f.write('  ' + '# The type of the relational database that is used.' + '\n')
                f.write('  ' + '# ' + '\n')
                f.write('  ' + '# The following table lists the possible values for this field:' + '\n')
                f.write('  ' + '# ' + '\n')
                f.write('  ' + '# | Value      | Description                                |' + '\n')
                f.write('  ' + '# | ---------- | ------------------------------------------ |' + '\n')
                f.write('  ' + '# | `postgres` | Uses PostgreSQL as the relational database |' + '\n')
                f.write('  ' + '# ' + '\n')
                f.write('  ' + '# Note, for use of `postgres`, it uses a [`postgres-controller` CRD](https://github.com/AlanBridgeman/postgres-controller) to create the database' + '\n')
                f.write('  ' + '# ' + '\n')
                f.write('  ' + f'type: "{database_template.type}"' + '\n')
                f.write('  ' + '\n')
                f.write('  ' + '# If set to `true`, the database will be created as part of the deployment' + '\n')
                f.write('  ' + '# This uses the [`postgres-controller` CRD](https://github.com/AlanBridgeman/postgres-controller) to create the database' + '\n')
                f.write('  ' + f'create: {str(database_template.create).lower()}' + '\n')
                f.write('  ' + '\n')
                f.write('  ' + '# The host that the database is located on ' + '\n')
                f.write('  ' + f'host: "{database_template.host}"' + '\n')
                f.write('  ' + '\n')
                f.write('  ' + '# The name of the database to be used' + '\n')
                f.write('  ' + f'name: "{database_template.name}"' + '\n')
                f.write('  ' + '\n')
                f.write('  ' + '# The user that is used to access the database' + '\n')
                f.write('  ' + f'user: "{database_template.user}"' + '\n')
                f.write('  ' + '\n')
                f.write('  ' + '# The password that is used to access the database' + '\n')
                f.write('  ' + f'password: "{database_template.password}"' + '\n')
                f.write('  ' + '\n')
                f.write('  ' + '# The port that the database listens on' + '\n')
                f.write('  ' + f'#port: {database_template.port}' + '\n')
                f.write('  ' + '\n')
                f.write('  ' + '# Allows for distinguishing between multiple database instances/servers' + '\n')
                f.write('  ' + f'#instance_id: "{database_template.instance_id}"' + '\n')
                f.write('\n')
            
            # If a Database template is included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, NoSQL) for template in self.templates):
                nosql_template = next(template for template in self.templates if isinstance(template, NoSQL))
                
                f.write('# Configuration the NoSQL database' + '\n')
                f.write('# Within the parlance of the system these are often called "properties" databases (and store less structured data)' + '\n')
                f.write('nosql:' + '\n')
                f.write('  ' + '# Determines the type of NoSQL storage that is used' + '\n')
                f.write('  ' + '# ' + '\n')
                f.write('  ' + '# The following table lists the possible values for this field:' + '\n')
                f.write('  ' + '# ' + '\n')
                f.write('  ' + '# | Value     | Description                                                                                |' + '\n')
                f.write('  ' + '# | --------- | ------------------------------------------------------------------------------------------ |' + '\n')
                f.write('  ' + '# | `mongodb` | Uses MongoDB as the NoSQL database for the default account properties database             |' + '\n')
                f.write('  ' + '# | `azure`   | Uses Azure Table Storage as the NoSQL database for the default account properties database |' + '\n')
                f.write('  ' + '# ' + '\n')
                f.write('  ' + f'type: {nosql_template.type}' + '\n')
                f.write('  ' + '\n')
                
                f.write('  ' + '# If to create a resource as part of the deployment process' + '\n')
                f.write('  ' + '# ONLY relevant if `type` is set to `mongodb`' + '\n')
                f.write('  ' + '# This uses the [MongoDBCommunity CRD](https://github.com/mongodb/mongodb-kubernetes-operator) to create the resource' + '\n')
                f.write('  ' + f'create: {str(nosql_template.create).lower()}' + '\n')
                f.write('  ' + '\n')
                
                f.write('  ' + '# The number of replicas/members as part of the Mongo deployment' + '\n')
                f.write('  ' + '# See the `member` parameter of the [MongoDBCommunity CRD](https://github.com/mongodb/mongodb-kubernetes-operator) for more information' + '\n')
                f.write('  ' + '# ONLY relevant if `type` is set to `mongodb` and `create` is set to `true`' + '\n')
                if isinstance(nosql_template, MongoDB):
                    f.write('  ' + f'replicaCount: {nosql_template.replica_count}' + '\n')
                else:
                    f.write('  ' + '#replicaCount: <Number of replicas>' + '\n')
                f.write('  ' + '\n')
                
                f.write('  ' + '# The TLS configuration for the connection to the NoSQL database' + '\n')
                f.write('  ' + '# ONLY relevant if `type` is set to `mongodb` and `create` is set to `true`' + '\n')
                f.write('  ' + 'tls:' + '\n')
                f.write('  ' + '  ' + '# If to use TLS for the connection to the NoSQL database' + '\n')
                if isinstance(nosql_template, MongoDB):
                    f.write('  ' + '  ' + f'enabled: {str(nosql_template.tls_enabled).lower()}' + '\n')
                else:
                    f.write('  ' + '  ' + 'enabled: <true/false>' + '\n')
                f.write('  ' + '\n')
                
                f.write('  ' + '# The connection string used to access the NoSQL database' + '\n')
                f.write('  ' + '# ONLY relevant if `type` is set to `mongodb` and `create` is set to `false`' + '\n')
                f.write('  ' + '# Should be in the following format: `mongodb://<hostname>:<port>`' + '\n')
                f.write('  ' + '#connectionString: "mongodb://mongo.example.com:27017"' + '\n')
                f.write('  ' + '\n')  
                
                f.write('  ' + '# The key used to access the NoSQL database' + '\n')
                f.write('  ' + '# ONLY relevant if `type` is set to `azure`' + '\n')
                f.write('  ' + '#key: ""' + '\n')
                f.write('  ' + '\n')
                
                f.write('  ' + '# The name of the NoSQL database' + '\n')
                f.write('  ' + f'name: "{nosql_template.db_name}"' + '\n')
                f.write('  ' + '\n')
                
                f.write('  ' + '# The username used to access the NoSQL database' + '\n')
                f.write('  ' + '# ONLY relevant if `type` is set to `mongodb`' + '\n')
                if isinstance(nosql_template, MongoDB):
                    f.write('  ' + f'user: "{nosql_template.user}"' + '\n')
                else:
                    f.write('  ' + 'user: "<mongo user>"' + '\n')
                f.write('  ' + '\n')
                
                f.write('  ' + '# The password used to access the NoSQL database' + '\n')
                f.write('  ' + '# ONLY relevant if `type` is set to `mongodb`' + '\n')
                if isinstance(nosql_template, MongoDB):
                    f.write('  ' + f'password: "{nosql_template.password}"' + '\n')
                else:
                    f.write('  ' + 'password: "<mongo password>"' + '\n')
                f.write('\n')
                
                f.write('# Configurable NoSQL information groupings' + '\n')
                f.write('# For Azure Table STorage these are table names' + '\n')
                f.write('# For MongoDB these are collection names' + '\n')
                f.write('tables:' + '\n')
                
                for value in nosql_template.tables.values():
                    snake_case_name = value['name'].split('-')[0]
                    for token in value['name'].split('-'):
                        if token != snake_case_name:
                            snake_case_name += token.capitalize()
                    f.write('  ' + f'{snake_case_name}: "{value["value"]}"' + '\n')
                #f.write('  ' + 'activityProperties: activity' + '\n')
                #f.write('  ' + 'eventProperties: eventProps' + '\n')
                #f.write('  ' + 'localeProperties: locales' + '\n')
                #f.write('  ' + 'organizerProperties: organizerProps' + '\n')
                #f.write('  ' + 'userProperties: userProps' + '\n')
                #f.write('  ' + 'templates: templates' + '\n')
                f.write('\n')
            
            # If a Redis template is included in the provided templates than we want to include the appropriate section to the values.yaml file.
            if any(isinstance(template, Redis) for template in self.templates):
                # Get the Redis template from the templates provided
                redis_template = next(template for template in self.templates if isinstance(template, Redis))
                
                f.write('# Configuration for cache server' + '\n')
                f.write('cache:' + '\n')
                f.write('  ' + 'type: "redis"' + '\n')
                f.write('  ' + '\n')

                f.write('  ' + '# If to create a Redis instance/resource as part of the deployment process' + '\n')
                f.write('  ' + f'create: {str(redis_template.create).lower()}' + '\n')
                f.write('  ' + '\n')

                f.write('  ' + '# The image to use for the Redis instance' + '\n')
                f.write('  ' + '# ONLY relevant if `create` is set to `true`' + '\n')
                # If the image dictionary is not empty than we want to include the image values
                if redis_template.create and len(redis_template.image) > 0:
                    f.write('  ' + 'image' + '\n')

                    # Loop through the image dictionary and write the image values
                    for key, value in redis_template.image.items():
                        f.write('  ' + '  ' + f'{key}: "{value}"' + '\n')
                else:
                    f.write('  ' + 'image: {}' + '\n')
                f.write('  ' + '\n')

                f.write('  ' + '# The number of replicas of the Redis instance' + '\n')
                f.write('  ' + '# ONLY relevant if `create` is set to `true`' + '\n')
                if redis_template.create:
                    f.write('  ' + f'replicaCount: {redis_template.replicaCount}' + '\n')
                else:
                    f.write('  ' + '#replicaCount: <Number of replicas (Ex. 1)>' + '\n')
                f.write('  ' + '\n')

                f.write('  ' + '# Hostname of the Redis server' + '\n')
                f.write('  ' + '# ONLY relevant if `create` is set to `false`' + '\n')
                if redis_template.create:
                    f.write('  ' + '#hostName: "<Redis Host Name>"' + '\n')
                else:
                    f.write('  ' + f'hostName: "{redis_template.hostName}"' + '\n')
                f.write('  ' + '\n')

                f.write('  ' + '# The password to use for the Redis server' + '\n')
                f.write('  ' + f'password: "{redis_template.password}"' + '\n')
                f.write('  ' + '\n')

                f.write('  ' + '# The port of the Redis server' + '\n')
                f.write('  ' + f'port: "{redis_template.port}"' + '\n')
                f.write('  ' + '\n')

                f.write('  ' + '# Redis TLS Configurations' + '\n')
                f.write('  ' + 'tls:' + '\n')
                f.write('  ' + '  ' + '# If TLS is enabled for the Redis instance' + '\n')
                f.write('  ' + '  ' + f'enabled: {str(redis_template.tls_enabled).lower()}' + '\n')
                f.write('  ' + '  ' + '\n')
                f.write('  ' + '  ' + '# The port of the Redis instance for TLS' + '\n')
                f.write('  ' + '  ' + '# ONLY relevant if `tls.enabled` is set to `true`' + '\n')
                if redis_template.tls_enabled:
                    f.write('  ' + '  ' + f'port: "{redis_template.tls_port}"' + '\n')
                else:
                    f.write('  ' + '  ' + '#port: "<TLS Port (Ex. 6380)>"' + '\n')
                f.write('  ' + '\n')
            
            f.write('# Configurations for integration with third-party services' + '\n')
            f.write('thirdParty:' + '\n')
            for template in self.templates:
                if isinstance(template, ThirdPartyService):
                    f.write('  ' + '# Configurations for the ' + template.name.capitalize() + ' integration' + '\n')
                    f.write('  ' + f'{template.name}:' + '\n')
                    f.write('  ' + '  ' + '# If the integration is enabled' + '\n')
                    f.write('  ' + '  ' + f'enabled: {str(template.enabled).lower()}' + '\n')
                    f.write('  ' + '  ' + '\n')
                    for key, value in template.vars.items():
                        snake_case_name = key.split('_')[0]
                        for token in key.split('_'):
                            if token != snake_case_name:
                                snake_case_name += token.capitalize()
                        f.write('  ' + '  ' + f'{snake_case_name}: {value}' + '\n')
                    f.write('  ' + '  ' + '\n')
            #f.write('  ' + '# Configuration for the OpenAI integration' + '\n')
            #f.write('  ' + 'openai:' + '\n')
            #f.write('  ' + '  ' + '# If the OpenAI integration is enabled' + '\n')
            #f.write('  ' + '  ' + 'enabled: true' + '\n')
            #f.write('  ' + '  ' + '\n')
            #f.write('  ' + '  ' + '# The OpenAI API key' + '\n')
            #f.write('  ' + '  ' + 'apiKey: ""' + '\n')
    
    def write_helmignore(self):
        with open('.helmignore', 'w') as f:
            f.write('# Ignore the ignore file' + '\n')
            f.write('.helmignore' + '\n')
            f.write('# Ignore the Helm chart\'s packaged tarball' + '\n')
            f.write('*.tgz' + '\n')
            f.write('# Ignore git files (In case done in the same directory as code)' + '\n')
            f.write('.git' + '\n')
            f.write('.gitignore' + '\n')
            f.write('# Ignore the README file (In case done in the same directory as code)' + '\n')
            f.write('README.md' + '\n')
            f.write('# Ignore the requirements file (In case done in the same directory as code)' + '\n')
            f.write('requirements.txt' + '\n')
            f.write('# Ignore this file (In case done in the same directory as code)' + '\n')
            f.write('create-helm-chart.py' + '\n')

    def package(self):
        """Package the Helm chart for publishing."""

        result = subprocess.run(['helm', 'package', '.'])

        if result.returncode != 0:
            raise Exception('Failed to package the Helm chart.')
    
    def push(self, registry: str):
        """Push the Helm chart to the Helm remote registry.
        
        Args:
            registry (str): The URL of the Helm remote registry
        """

        if not os.path.exists(f'{self.chartName}-{self.chartVersion}.tgz'):
            raise Exception('The Helm chart has not been packaged yet.')
        
        print(f'Pushing {self.chartName}-{self.chartVersion}.tgz to {registry}')
        
        subprocess.run(['helm', 'push', f'{self.chartName}-{self.chartVersion}.tgz', f'oci://{registry}'])
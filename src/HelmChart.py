import os, subprocess

from .Template import Template
from .Ingress import Ingress
from .Database import Database
from .NoSQL import NoSQL
from .MongoDB import MongoDB
from .AzureTableStorage import AzureTableStorage
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
        """Write the Chart.yaml file for the Helm chart.
        
        This provides the metadata about the Helm chart itself.
        """

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
    
    def create_replicas_section_of_values_yaml(self) -> str:
        """Create the replicas section of the `values.yaml` file for the Helm chart.

        Unlike most of the other `create_..._section_of_values_yaml` methods, 
        the "replicas" section isn't an actual "section" in the sense that it doesn't have subfields of a `replica` field.
        Instead, it's just a (or a set of) fields straight under the root of the `values.yaml` file.

        Particularly, at time of writing the `replicaCount` field which is how many replicas of the app to run.
        
        Returns:
            str: The replicas section of the `values.yaml` file
        """

        output = ''

        # Get the Deployment templates from the templates provided
        deployment_template = next(template for template in self.templates if isinstance(template, Deployment))

        output += '# The number of instances (replicas) of the app to run' + '\n'
        output += f'replicaCount: {deployment_template.replica_count}' + '\n'
        output += '\n'

        return output

    def create_image_section_of_values_yaml(self) -> str:
        """Create the image section of the `values.yaml` file for the Helm chart.
        
        The image section is used to define the image that the app will use.

        Returns:
            str: The image section of the `values.yaml` file
        """

        output = ''

        # Get the Deployment templates from the templates provided
        deployment_template = next(template for template in self.templates if isinstance(template, Deployment))

        output += 'image:' + '\n'
        output += '  ' + '# The repository of the image to use for the app' + '\n'
        output += '  ' + '# Should be in the format `<Image Repository (Ex. containers.example.com)>/<Image Name (Ex. app)>`' + '\n'
        output += '  ' + f'repository: "{deployment_template.image_repository}"' + '\n'
        output += '  ' + '# The specific image tag to use. It\'s recommended to use some kind of versioning tag scheme as it makes updating the container without having to fully redeploy easier.' + '\n'
        output += '  ' + '# Ex. v1.0.0' + '\n'
        output += '  ' + f'tag: "{deployment_template.image_tag}"' + '\n'
        output += '  ' + '# How often the image should be pulled. The possible values are "Always", "Never", and "IfNotPresent"' + '\n'
        output += '  ' + '# It\'s recommended for production to use "IfNotPresent" to avoid pulling the image every time the pod starts' + '\n'
        output += '  ' + '# Though, for development, "Always" is recommended to ensure the latest changes are being tested' + '\n'
        output += '  ' + f'pullPolicy: "{deployment_template.image_pull_policy}"' + '\n'
        output += '\n'

        return output

    def create_container_section_of_values_yaml(self) -> str:
        """Create the container section of the `values.yaml` file for the Helm chart.
        
        The container section is used to define the environment that the container is running in.
        Ex. the environment type (development, production, etc...) and the port that the container listens on.

        Returns:
            str: The container section of the `values.yaml` file
        """

        output = ''

        # Get the Deployment templates from the templates provided
        deployment_template = next(template for template in self.templates if isinstance(template, Deployment))

        output += 'container:' + '\n'
        output += '  ' + '# The port that the container listens on (Ex. 8080)' + '\n'
        output += '  ' + f'port: {deployment_template.port}' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# The environment that the container is running in (Ex. development, production, etc...)' + '\n'
        output += '  ' + '# This is used for the NODE_ENV environment variable' + '\n'
        output += '  ' + f'env: "{deployment_template.env}"' + '\n'
        output += '\n'

        return output

    def create_ingress_section_of_values_yaml(self) -> str:
        """Create the ingress section of the `values.yaml` file for the Helm chart.
        
        The ingress section is used to define the ingress resource that the app will use.
        That is how the app will be accessed from outside the cluster.

        Returns:
            str: The ingress section of the `values.yaml` file
        """

        output = ''

        # Get the Ingress templates from the templates provided
        ingress_template = next(template for template in self.templates if isinstance(template, Ingress))

        output += 'ingress:' + '\n'
        output += '  ' + '# We want an ingress resource if we are deploying to a cluster that has a ingress controller/load balancer' + '\n'
        output += '  ' + '# This includes most public cloud providers like EKS, GKE, and AKS' + '\n'
        output += '  ' + 'enabled: true' + '\n'
        output += '  ' + '# The DNS Name (Ex. app.example.com) where the app will be accessible' + '\n'
        output += '  ' + f'host: "{ingress_template.hostname}"' + '\n'
        output += '  ' + '# The class of the ingress controller that is being used (defaulted here to an NGINX ingress controller as it\'s popular for Kubernetes clusters)' + '\n'
        output += '  ' + 'class: nginx' + '\n'
        output += '\n'

        return output
    
    def create_deployment_extra_vars_section_of_values_yaml(self) -> str:
        """Create the extra environment variables for the deployment section of the `values.yaml` file for the Helm chart.
        
        Somewhat similar to the "replicas" section, the "extra environment variables" aren't a real "section" in the sense that they don't have subfields of an `extraEnvVars` field.

        The extra environment variables are used to define additional environment variables that the deployment will use.
        This is useful for providing extra configuration to the app that is being deployed.

        Returns:
            str: The extra environment variables section of the `values.yaml` file
        """

        output = ''

        # Get the Deployment templates from the templates provided
        deployment_template = next(template for template in self.templates if isinstance(template, Deployment))

        for value in deployment_template.extra_env_vars.values():
            if isinstance(value, dict):
                # If a description is provided for the environment variable than we want to include it as a comment above the value in the `values.yaml` file.
                if 'description' in value:
                    output += f'# {value["description"]}' + '\n'
                
                # Because the name given within the value in the dictionary is intended as the unique name of the configmap/secret that contains the value 
                # It usually contains a reference to the Helm release name.
                # However, here we want the name without this component so we do a string replacement to remove it.
                var_name = value["name"].replace('{{ .Release.Name }}-', '')

                # We want to convert the name to camelCase because this is our convention for `values.yaml` keys
                camel_case_name = var_name.split('-')[0]
                for token in var_name.split('-'):
                    if token != camel_case_name:
                        camel_case_name += token.capitalize()
                    
                output += f'{camel_case_name}: "{value["value"]}"' + '\n'
            
            # For readability of the `values.yaml` file we put an extra line between each extra deployment environment variable
            output += '\n'

        return output
    
    def create_oauth_section_of_values_yaml(self) -> str:
        """Create the OAuth section of the `values.yaml` file for the Helm chart.

        The OAuth section is used to define the OAuth configuration that the app will use.
        This is useful for providing OAuth configuration to the app that is being deployed.

        Note, this assumes the app uses the Bridgeman Accessible OAuth implementation etc...

        Returns:
            str: The OAuth section of the `values.yaml` file
        """

        output = ''

        # Get the OAuth template from the templates provided
        oauth_template = next(template for template in self.templates if isinstance(template, OAuth))

        output += '# Configuration for using OAuth within the app' + '\n'
        output += 'oauth:' + '\n'
        output += '  ' + f'baseAppUrl: "{oauth_template.base_app_url}"' + '\n'
        output += '  ' + f'appAbbreviation: "{oauth_template.app_abbreviation}"' + '\n'
        output += '  ' + f'appName: "{oauth_template.app_name}"' + '\n'
        output += '  ' + f'serviceName: "{oauth_template.service_name}"' + '\n'
        output += '  ' + f'devPort: "{oauth_template.dev_port}"' + '\n'
        output += '\n'

        return output
    
    def create_database_section_of_values_yaml(self) -> str:
        """Create the Database section of the `values.yaml` file for the Helm chart.

        The Database section is used to define the database configuration that the app will use.

        Returns:
            str: The Database section of the `values.yaml` file
        """

        output = ''
        
        # Get the Database template from the templates provided
        database_template = next(template for template in self.templates if isinstance(template, Database))

        output += '# Configuration for the relational database' + '\n'
        output += 'database:' + '\n'
        output += '  ' + '# The type of the relational database that is used.' + '\n'
        output += '  ' + '# ' + '\n'
        output += '  ' + '# The following table lists the possible values for this field:' + '\n'
        output += '  ' + '# ' + '\n'
        output += '  ' + '# | Value      | Description                                |' + '\n'
        output += '  ' + '# | ---------- | ------------------------------------------ |' + '\n'
        output += '  ' + '# | `postgres` | Uses PostgreSQL as the relational database |' + '\n'
        output += '  ' + '# ' + '\n'
        output += '  ' + '# Note, for use of `postgres`, it uses a [`postgres-controller` CRD](https://github.com/AlanBridgeman/postgres-controller) to create the database' + '\n'
        output += '  ' + '# ' + '\n'
        output += '  ' + f'type: "{database_template.type}"' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# If set to `true`, the database will be created as part of the deployment' + '\n'
        output += '  ' + '# This uses the [`postgres-controller` CRD](https://github.com/AlanBridgeman/postgres-controller) to create the database' + '\n'
        output += '  ' + f'create: {str(database_template.create).lower()}' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# The host that the database is located on ' + '\n'
        output += '  ' + f'host: "{database_template.host}"' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# The name of the database to be used' + '\n'
        output += '  ' + f'name: "{database_template.name}"' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# The user that is used to access the database' + '\n'
        output += '  ' + f'user: "{database_template.user}"' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# The password that is used to access the database' + '\n'
        output += '  ' + f'password: "{database_template.password}"' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# The port that the database listens on' + '\n'
        output += '  ' + f'#port: {database_template.port}' + '\n'
        output += '  ' + '\n'
        output += '  ' + '# Allows for distinguishing between multiple database instances/servers' + '\n'
        output += '  ' + f'#instance_id: "{database_template.instance_id}"' + '\n'
        output += '\n'

        return output
    
    def create_nosql_section_of_values_yaml(self) -> str:
        """Create the NoSQL section of the `values.yaml` file for the Helm chart.

        The NoSQL section is used to define the NoSQL storage configuration that the app will use.

        Returns:
            str: The NoSQL section of the `values.yaml` file
        """

        output = ''

        nosql_template = next(template for template in self.templates if isinstance(template, NoSQL))
                
        output += '# Configuration the NoSQL database' + '\n'
        output += '# Within the parlance of the system these are often called "properties" databases (and store less structured data)' + '\n'
        output += 'nosql:' + '\n'
        output += '  ' + '# Determines the type of NoSQL storage that is used' + '\n'
        output += '  ' + '# ' + '\n'
        output += '  ' + '# The following table lists the possible values for this field:' + '\n'
        output += '  ' + '# ' + '\n'
        output += '  ' + '# | Value     | Description                                                                                |' + '\n'
        output += '  ' + '# | --------- | ------------------------------------------------------------------------------------------ |' + '\n'
        output += '  ' + '# | `mongodb` | Uses MongoDB as the NoSQL database for the default account properties database             |' + '\n'
        output += '  ' + '# | `azure`   | Uses Azure Table Storage as the NoSQL database for the default account properties database |' + '\n'
        output += '  ' + '# ' + '\n'
        output += '  ' + f'type: {nosql_template.type}' + '\n'
        output += '  ' + '\n'
                
        output += '  ' + '# If to create a resource as part of the deployment process' + '\n'
        output += '  ' + '# ONLY relevant if `type` is set to `mongodb`' + '\n'
        output += '  ' + '# This uses the [MongoDBCommunity CRD](https://github.com/mongodb/mongodb-kubernetes-operator) to create the resource' + '\n'
        output += '  ' + f'create: {str(nosql_template.create).lower()}' + '\n'
        output += '  ' + '\n'
                
        output += '  ' + '# The number of replicas/members as part of the Mongo deployment' + '\n'
        output += '  ' + '# See the `member` parameter of the [MongoDBCommunity CRD](https://github.com/mongodb/mongodb-kubernetes-operator) for more information' + '\n'
        output += '  ' + '# ONLY relevant if `type` is set to `mongodb` and `create` is set to `true`' + '\n'
        if isinstance(nosql_template, MongoDB):
            output += '  ' + f'replicaCount: {nosql_template.replica_count}' + '\n'
        else:
            output += '  ' + '#replicaCount: <Number of replicas>' + '\n'
        output += '  ' + '\n'
                
        output += '  ' + '# The TLS configuration for the connection to the NoSQL database' + '\n'
        output += '  ' + '# ONLY relevant if `type` is set to `mongodb` and `create` is set to `true`' + '\n'
        output += '  ' + 'tls:' + '\n'
        output += '  ' + '  ' + '# If to use TLS for the connection to the NoSQL database' + '\n'
        if isinstance(nosql_template, MongoDB):
            output += '  ' + '  ' + f'enabled: {str(nosql_template.tls_enabled).lower()}' + '\n'
        else:
            output += '  ' + '  ' + 'enabled: <true/false>' + '\n'
        output += '  ' + '\n'
                
        output += '  ' + '# The connection string used to access the NoSQL database' + '\n'
        output += '  ' + '# ONLY relevant if `type` is set to `mongodb` and `create` is set to `false`' + '\n'
        output += '  ' + '# Should be in the following format: `mongodb://<hostname>:<port>`' + '\n'
        output += '  ' + '#connectionString: "mongodb://mongo.example.com:27017"' + '\n'
        output += '  ' + '\n'
                
        output += '  ' + '# The key used to access the NoSQL database' + '\n'
        output += '  ' + '# ONLY relevant if `type` is set to `azure`' + '\n'
        if isinstance(nosql_template, AzureTableStorage):
            output += '  ' + f'key: "{nosql_template.key}"' + '\n'
        else:
            output += '  ' + '#key: ""' + '\n'
        output += '  ' + '\n'
        
        output += '  ' + '# The name of the NoSQL database' + '\n'
        output += '  ' + f'name: "{nosql_template.db_name}"' + '\n'
        output += '  ' + '\n'
                
        output += '  ' + '# The username used to access the NoSQL database' + '\n'
        output += '  ' + '# ONLY relevant if `type` is set to `mongodb`' + '\n'
        if isinstance(nosql_template, MongoDB):
            output += '  ' + f'user: "{nosql_template.user}"' + '\n'
        else:
            output += '  ' + 'user: "<mongo user>"' + '\n'
        output += '  ' + '\n'
                
        output += '  ' + '# The password used to access the NoSQL database' + '\n'
        output += '  ' + '# ONLY relevant if `type` is set to `mongodb`' + '\n'
        if isinstance(nosql_template, MongoDB):
            output += '  ' + f'password: "{nosql_template.password}"' + '\n'
        else:
            output += '  ' + 'password: "<mongo password>"' + '\n'
        output += '\n'
                
        output += '# Configurable NoSQL information groupings' + '\n'
        output += '# For Azure Table Storage these are table names' + '\n'
        output += '# For MongoDB these are collection names' + '\n'
        output += 'tables:' + '\n'
                
        for value in nosql_template.tables.values():
            camel_case_name = value['name'].split('-')[0]
            for token in value['name'].split('-'):
                if token != camel_case_name:
                    camel_case_name += token.capitalize()
            
            output += '  ' + f'{camel_case_name}: "{value["value"]}"' + '\n'
                
        output += '\n'

        return output

    def create_cache_section_of_values_yaml(self) -> str:
        """Create the Cache section of the `values.yaml` file for the Helm chart.

        The Cache section is used to define the cache (usually Redis) configuration that the app will use.

        Returns:
            str: The Cache section of the `values.yaml` file
        """

        output = ''
        
        # Get the Redis template from the templates provided
        redis_template = next(template for template in self.templates if isinstance(template, Redis))
                
        output += '# Configuration for cache server' + '\n'
        output += 'cache:' + '\n'
        output += '  ' + 'type: "redis"' + '\n'
        output += '  ' + '\n'

        output += '  ' + '# If to create a Redis instance/resource as part of the deployment process' + '\n'
        output += '  ' + f'create: {str(redis_template.create).lower()}' + '\n'
        output += '  ' + '\n'

        output += '  ' + '# The image to use for the Redis instance' + '\n'
        output += '  ' + '# ONLY relevant if `create` is set to `true`' + '\n'
        # If the image dictionary is not empty than we want to include the image values
        if redis_template.create and len(redis_template.image) > 0:
            output += '  ' + 'image' + '\n'

            # Loop through the image dictionary and write the image values
            for key, value in redis_template.image.items():
                output += '  ' + '  ' + f'{key}: "{value}"' + '\n'
        else:
            output += '  ' + 'image: {}' + '\n'
        output += '  ' + '\n'

        output += '  ' + '# The number of replicas of the Redis instance' + '\n'
        output += '  ' + '# ONLY relevant if `create` is set to `true`' + '\n'
        if redis_template.create:
            output += '  ' + f'replicaCount: {redis_template.replicaCount}' + '\n'
        else:
            output += '  ' + '#replicaCount: <Number of replicas (Ex. 1)>' + '\n'
        output += '  ' + '\n'

        output += '  ' + '# Hostname of the Redis server' + '\n'
        output += '  ' + '# ONLY relevant if `create` is set to `false`' + '\n'
        if redis_template.create:
            output += '  ' + '#hostName: "<Redis Host Name>"' + '\n'
        else:
            output += '  ' + f'hostName: "{redis_template.hostName}"' + '\n'
        output += '  ' + '\n'

        output += '  ' + '# The password to use for the Redis server' + '\n'
        output += '  ' + f'password: "{redis_template.password}"' + '\n'
        output += '  ' + '\n'

        output += '  ' + '# The port of the Redis server' + '\n'
        output += '  ' + f'port: "{redis_template.port}"' + '\n'
        output += '  ' + '\n'

        output += '  ' + '# Redis TLS Configurations' + '\n'
        output += '  ' + 'tls:' + '\n'
        output += '  ' + '  ' + '# If TLS is enabled for the Redis instance' + '\n'
        output += '  ' + '  ' + f'enabled: {str(redis_template.tls_enabled).lower()}' + '\n'
        output += '  ' + '  ' + '\n'
        output += '  ' + '  ' + '# The port of the Redis instance for TLS' + '\n'
        output += '  ' + '  ' + '# ONLY relevant if `tls.enabled` is set to `true`' + '\n'
        if redis_template.tls_enabled:
            output += '  ' + '  ' + f'port: "{redis_template.tls_port}"' + '\n'
        else:
            output += '  ' + '  ' + '#port: "<TLS Port (Ex. 6380)>"' + '\n'
        output += '  ' + '\n'

        return output
    
    def create_third_party_service_section_of_values_yaml(self) -> str:
        """Create the Third Party Service section of the `values.yaml` file for the Helm chart.

        The Third Party Service section is used to define any third-party service configurations that the app will use.
        Ex. OpenAI, Stripe, etc...

        Returns:
            str: The Third Party Service section of the `values.yaml` file
        """

        output = ''
        
        output += '# Configurations for integration with third-party services' + '\n'
        output += 'thirdParty:' + '\n'
        for template in self.templates:
            if isinstance(template, ThirdPartyService):
                output += '  ' + '# Configurations for the ' + template.name.capitalize() + ' integration' + '\n'
                output += '  ' + f'{template.name}:' + '\n'
                output += '  ' + '  ' + '# If the integration is enabled' + '\n'
                output += '  ' + '  ' + f'enabled: {str(template.enabled).lower()}' + '\n'
                output += '  ' + '  ' + '\n'
                for key, value in template.vars.items():
                    camel_case_name = key.split('_')[0]
                    for token in key.split('_'):
                        if token != camel_case_name:
                            camel_case_name += token.capitalize()
                    
                    output += '  ' + '  ' + f'{camel_case_name}: {value}' + '\n'
                output += '  ' + '  ' + '\n'

    def write_values_yaml(self):
        """Write the `values.yaml` file for the Helm chart.
        
        Note, that this generates a `values.yaml` file that is specific to the templates provided.
        This means, that it's generally better for usage than distribution.

        In other words, because it's likely it could contain sensitive information, it's not recommended to distribute this file (or include it in git etc...)
        """

        with open('values.yaml', 'w') as f:
            # replicas section (mostly just `replicaCount` but...)
            f.write(self.create_replicas_section_of_values_yaml())
            
            # image section
            f.write(self.create_image_section_of_values_yaml())
            
            # container section
            f.write(self.create_container_section_of_values_yaml())
            
            # ingress section
            f.write(self.create_ingress_section_of_values_yaml())
            
            # Add the extra environment variables for the deployment to the `values.yaml` file
            f.write(self.create_deployment_extra_vars_section_of_values_yaml())

            # If a OAuth template is included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, OAuth) for template in self.templates):
                f.write(self.create_oauth_section_of_values_yaml())
            
            # If a Database template is included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, Database) for template in self.templates):
                f.write(self.create_database_section_of_values_yaml())
            
            # If a Database template is included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, NoSQL) for template in self.templates):
                f.write(self.create_nosql_section_of_values_yaml())
            
            # If a Redis template is included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, Redis) for template in self.templates):
                f.write(self.create_cache_section_of_values_yaml())
            
            # If any Third Party Service templates are included in the provided templates than we want to include the appropriate section to the `values.yaml` file.
            if any(isinstance(template, ThirdPartyService) for template in self.templates):
                f.write(self.create_third_party_service_section_of_values_yaml())
    
    def write_helmignore(self):
        """Write the .helmignore file for the Helm chart.
        
        This file is used to ignore files that are not needed in the Helm chart.
        This makes the chart smaller and more efficient.
        """

        with open('.helmignore', 'w') as f:
            f.write('# Ignore the ignore file' + '\n')
            f.write('.helmignore' + '\n')
            
            f.write('# Ignore the Helm chart\'s packaged tarball' + '\n')
            f.write('*.tgz' + '\n')
            
            if os.path.exists('.git'):
                f.write('# Ignore git files (In case done in the same directory as code)' + '\n')
                f.write('.git' + '\n')
            
            if os.path.exists('.gitignore'):
                f.write('.gitignore' + '\n')
            
            if os.path.exists('README.md'):
                f.write('# Ignore the README file (In case done in the same directory as code)' + '\n')
                f.write('README.md' + '\n')
            
            if os.path.exists('requirements.txt'):
                f.write('# Ignore the requirements file (In case done in the same directory as code)' + '\n')
                f.write('requirements.txt' + '\n')
            
            if os.path.exists('create-helm-chart.py'):
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
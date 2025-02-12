import json

from src.Ingress import Ingress
from src.Service import Service
from src.Database import Database
from src.HashicorpVault import HashicorpVault
from src.MongoDB import MongoDB
from src.Redis import Redis
from src.OAuth import OAuth
from src.ThirdPartyService import ThirdPartyService
from src.Deployment import Deployment
from src.HelmChart import HelmChart

if __name__ == '__main__':
    with open('input.json', 'r') as f:
        data = json.load(f)
    
    # The API version of the Helm chart itself
    api_version = data['chart']['apiVersion']
    # The version of the application that the Helm chart is deploying
    app_version = data['chart']['appVersion']
    # A description of the Helm chart
    chart_description = data['chart']['description']
    # The URL of the Helm chart's home page
    chart_homepage = data['chart']['homepage']
    # The maintainers of the Helm chart
    maintainers = data['chart']['maintainers']
    # The name of the Helm chart
    chart_name = data['chart']['name']
    # The sources of the Helm chart
    sources = data['chart']['sources']
    # The version of the Helm chart
    chart_version = data['chart']['version']

    image_repository = data['image']['repository']
    image_pull_policy = data['image']['pullPolicy']
    
    hostname = data['ingress']['hostname']

    ingress = Ingress(hostname)
    service = Service()

    templates = [ingress, service]

    uses_db = False
    uses_secrets_vault = False
    nosql = None
    uses_cache = False
    third_party_services = []
    extra_env_vars = {}

    if 'db' in data and data['db'] != False:
        db_name = data['db']['name']
        db_host = data['db']['host']
        db_user = data['db']['user']
        db_password = data['db']['password']

        db = Database(db_name, db_host, db_user, db_password)

        uses_db = True

        templates.append(db)
    
    if 'vault' in data and data['vault'] != False:
        vault_image = {
            'repository': data['vault']['image']['repository'],
            'tag': data['vault']['image']['tag']
        }
        vault_hostname = data['vault']['hostname']
        vault_storage_class = data['vault']['storageClass']

        vault = HashicorpVault(image=vault_image, hostname=vault_hostname, storage_class=vault_storage_class)

        uses_secrets_vault = True

        templates.append(vault)
    
    if 'nosql' in data and data['nosql'] != False:
        nosql_db_name = data['nosql']['dbName']
        nosql_user = data['nosql']['user']
        nosql_password = data['nosql']['password']

        tables = data['nosql']['tables']

        mongo = MongoDB(nosql_db_name, nosql_user, nosql_password, tables)

        nosql = mongo

        templates.append(mongo)

    if 'cache' in data and data['cache'] != False:
        cache_password = data['cache']['password']

        redis = Redis(cache_password)

        uses_cache = True

        templates.append(redis)
    
    if 'oauth' in data and data['oauth'] != False:
        base_app_url = data['oauth']['baseAppUrl']
        app_abbreviation = data['oauth']['appAbbreviation']
        app_name = data['oauth']['appName']
        service_name = data['oauth']['serviceName']
        dev_port = data['oauth']['devPort']

        oauth = OAuth(base_app_url, app_abbreviation, app_name, service_name, dev_port)

        templates.append(oauth)
    
    if 'thirdPartyServices' in data:
        if 'openai' in data['thirdPartyServices']:
            openai_api_key = data['thirdPartyServices']['openai']['apiKey']

            openai = ThirdPartyService('openai', False, api_key=openai_api_key)

            third_party_services.append(openai)

            templates.append(openai)
        
        if 'stripe' in data['thirdPartyServices']:
            stripe_public_key = data['thirdPartyServices']['stripe']['publicKey']
            stripe_secret_key = data['thirdPartyServices']['stripe']['secretKey']
            stripe_test_public_key = data['thirdPartyServices']['stripe']['testPublicKey']
            stripe_test_secret_key = data['thirdPartyServices']['stripe']['testSecretKey']

            stripe = ThirdPartyService('stripe', True, public_key=stripe_public_key, secret_key=stripe_secret_key, test_public_key=stripe_test_public_key, test_secret_key=stripe_test_secret_key)

            third_party_services.append(stripe)

            templates.append(stripe)

    if 'extraEnvVars' in data:
        extra_env_vars = data['extraEnvVars']
        for key, value in extra_env_vars.items():
            if not isinstance(value, dict) and value.find("'") != -1:
                extra_env_vars[key] = value.replace("'", '"')

    
    deployment = Deployment(image_repository, image_pull_policy=image_pull_policy, uses_db=uses_db, uses_secrets_vault=uses_secrets_vault, nosql=nosql, uses_cache=uses_cache, third_party_services=third_party_services, **extra_env_vars)
    templates.append(deployment)

    #templates = [ingress, service, db, vault, mongo, redis, oauth, deployment, stripe, openai]
    
    helmChart = HelmChart(chart_name, chart_description, maintainers, chart_homepage, sources, app_version, chart_version, api_version, *templates)
    helmChart.create_templates_folder()
    helmChart.write_yaml()
    helmChart.write_values_yaml()
    helmChart.write_helmignore()
    
    try:
        helmChart.package()

        if 'registry' in data:
            helm_registry = data['registry']
            try:
                helmChart.push(helm_registry)
            except Exception as ex:
                print('Push to the registry failed. Please check the error message below:')
                print(ex)
    except Exception as e:
        print('Packaging the Helm chart failed. Please check the error message below:')
        print(e)

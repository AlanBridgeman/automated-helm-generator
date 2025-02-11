import json

from src.Ingress import Ingress
from src.Service import Service
from src.Database import Database
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

    db_name = data['db']['name']
    db_host = data['db']['host']
    db_user = data['db']['user']
    db_password = data['db']['password']

    nosql_db_name = data['nosql']['dbName']
    nosql_user = data['nosql']['user']
    nosql_password = data['nosql']['password']
    
    tables = data['nosql']['tables']

    cache_password = data['cache']['password']

    base_app_url = data['oauth']['baseAppUrl']
    app_abbreviation = data['oauth']['appAbbreviation']
    app_name = data['oauth']['appName']
    service_name = data['oauth']['serviceName']
    dev_port = data['oauth']['devPort']
    client_id = data['oauth']['clientId']
    client_secret = data['oauth']['clientSecret']

    extra_env_vars = data['extraEnvVars']
    for key, value in extra_env_vars.items():
        if not isinstance(value, dict) and value.find("'") != -1:
            extra_env_vars[key] = value.replace("'", '"')
    
    openai_api_key = data['thirdPartyServices']['openai']['apiKey']

    helm_registry = data['registry']

    ingress = Ingress(hostname)
    service = Service()
    db = Database(db_name, db_host, db_user, db_password)
    mongo = MongoDB(nosql_db_name, nosql_user, nosql_password, tables)
    redis = Redis(cache_password)
    oauth = OAuth(base_app_url, app_abbreviation, app_name, service_name, dev_port, client_id, client_secret)
    openai = ThirdPartyService('openai', True, api_key=openai_api_key)
    deployment = Deployment(image_repository, image_pull_policy=image_pull_policy, uses_db=True, nosql=mongo, uses_cache=True, third_party_services=[openai], **extra_env_vars)
    templates = [ingress, service, db, mongo, redis, oauth, deployment, openai]
    helmChart = HelmChart(chart_name, chart_description, maintainers, chart_homepage, sources, app_version, chart_version, api_version, *templates)
    helmChart.create_templates_folder()
    helmChart.write_yaml()
    helmChart.write_values_yaml()
    helmChart.write_helmignore()
    
    try:
        helmChart.package()

        try:
            helmChart.push(helm_registry)
        except Exception as ex:
            print('Push to the registry failed. Please check the error message below:')
            print(ex)
    except Exception as e:
        print('Packaging the Helm chart failed. Please check the error message below:')
        print(e)

# Automated Helm Chart Generator
This is a relatively simplistic Python app to simplify creating a Helm Chart more easily.

Keep in mind, this is fairly opinionated and simplistic in it's implementation. This is on purpose. This largely developed for my own use rather than general applicability.

## Getting Started
In general, there are 3 steps to run this automatation: 
1. Run the appropriate installer script (technically this isn't required as you could just run the Python script directly but is for convenience)
2. Create and customize a `input.json` file that has the inputs for the script
3. Run the script

### On Windows
Run the followng
```PowerShell
.\install.ps1
```

Next copy the `input.example.json` into the folder you want (replacing `<Folder for Helm Chart>` with the appropriate path) and rename it `input.json`. You'll also probably want to customize this file (though not technically required)
```PowerShell
Copy-Item input.example.json <Folder for Helm Chart>\input.json
```

Then in the directory you want
```PowerShell
create-helm-chart
```

### On Mac/Linux (Uses Bash)
Run the followng
```sh
./install.sh
```

Next copy the `input.example.json` into the folder you want (replacing `<Folder for Helm Chart>` with the appropriate path) and rename it `input.json`. You'll also probably want to customize this file (though not technically required)
```sh
cp ./input.example.json <Folder for Helm Chart>/input.json
```

Then in the directory you want
```sh
create-helm-chart
```

## Inputs File (`input.json`)
The most basic version is below. Note values between `<>` should be replaced with appropriate values.

```json
{
    "chart": {
        "apiVersion": "v1",
        "appVersion": "1.0.0",
        "description": "A Helm chart for deploying <service name>.",
        "homepage": "<Helm Chart Homepage>",
        "maintainers": [
            {
                "name": "<Author Name>", 
                "email": "<Author Email>"
            }
        ],
        "name": "<Helm Chart Name>",
        "sources": [
            "<Helm Chart Source>"
        ],
        "version": "1.0.0"
    },
    "image": {
        "repository": "<Registry URL (if applicable)>/<Image Name>",
        "pullPolicy": "IfNotPresent"
    },
    "ingress": {
        "hostname": "<DNS Name Where The App Will Be Hosted>"
    }
}
```

### Database (Postgres)
To add a Postgres database include the following in the `inputs.json` file and fill out the values.

```json
{
    "db": {
        "name": "<Database Name>",
        "host": "<Database Host>",
        "user": "<Database User>",
        "password": "<Database Password>"
    }
}
```

### Secrets Vault (Hashicorp Vault)
To add a Hashicorp secrets vault include the following in the `inputs.json` file and fill out the values

```json
{
    "vault": {
        "image": {
            "repository": "<Vault Image Repository>",
            "tag": "<Vault Image Tag>"
        },
        "hostname": "<DNS Name where the vault will be hosted>",
        "storageClass": "<Storage Class Name>"
    }
}
```

### NoSQL Storage (Mongo)
To add a Mongo instance include the following in the `inputs.json` file and fill out the values.

```json
{
    "nosql": {
        "dbName": "<NoSQL Database Name>",
        "user": "<NoSQL Database User>",
        "password": "<NoSQL Database Password>",
        "tables": {
            "<Table Environment Variable Name>": {
                "name": "<Table Intermediate Name (used in Helm template files)>",
                "value": "<Actual Table Name>"
            }
        }
    }
}
```

### Cache Database (Redis)
To add a Redis instance include the following in the `inputs.json` file and fill out the values.

```json
{
    "cache": {
        "password": "<Cache Password>"
    }
}
```

### OAuth
To add the OAuth variables include the following in the `inputs.json` file and fill out the values.

```json
{
    "oauth": {
        "baseAppUrl": "<Base URL of the App>",
        "appAbbreviation": "<App Abbreviation>",
        "appName": "<App Name>",
        "serviceName": "<Service Name>",
        "devPort": "<Dev Port>"
    }
}
```

### Third Party Services

```json
{
    "thirdPartyServices": {
        "openai": {
            "apiKey": "<OpenAI API Key>"
        },
        "stripe": {
            "publicKey": "<Stripe Public Key>",
            "secretKey": "<Stripe Secret Key>",
            "testPublicKey": "<Stripe Test Public Key>",
            "testSecretKey": "<Stripe Test Secret Key>"
        }
    }
}
```

### Extra/Other Environment Variables

```json
{
    "extraEnvVars": {
        "<Sensitive Environment Variable Name>": {
            "type": "Secret",
            "name": "{{ .Release.Name }}-<Sensitive Value Name (ex. private-token, etc...)>",
            "key": "<Key Used Within The Secret (ex. token, etc...)>",
            "description": "<Description Of The Environment Variable>",
            "value": "<Value for the Environment Variable>"
        },
        "<Configurable Environment Variable Name>": {
            "type": "ConfigMap",
            "name": "{{ .Release.Name }}-<Configurable Value Name (ex. external-service-host, etc...)>",
            "key": "<Key Used Within The ConfigMap (ex. extern-host, etc...)>",
            "description": "<Description Of The Environment Variable>",
            "value": "<Value for the Environment Variable>"
        },
        "<Environment Variable Name>": "'<Quoted Value>'"
    }
}
```

### Helm Resitry (for pushing)

```json
{
    "registry": "<Helm Registry URL to publish to (if applicable)>"
}
```
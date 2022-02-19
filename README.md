# AIQ1 API deployment pipeline in GKE using Google Cloud Endpoints (OpenAPI version)

````
aiq_1/
├── README.md
├── cloudbuild.yaml
├── Dockerfile
├── requirements.txt
├── manage.py
│
├── endpoint
│    ├── endpoint-config.sh
│    └── openapi.yaml
│
├── k8s
│    ├── endpoint-deployment.yaml
│    └── service.yaml
│
├── resources
│    ├── application-test.yaml
│    └── egrid2016_data.yaml
│
└── app
    │ 
    ├── configuration.py
    └── src 
        ├── controller
        │    └── namespace_api.py
        │ 
        ├── exceptions
        │   └── exceptions.py
        │ 
        ├── model
        │   └── model.py
        │ 
        └── service
            └── service.py

````

## Application

This application exposes a service that returns the top U.S N plants in termns of power
produced in 2016, State filter optional.


## Flask application

The Flask app is managed by the manage.py python file, that will load the application from a create_app method that 
will load the configuration and expose the endpoints /check and /service 

```python
    <...>
flask_app = create_app('resources/application-test.yml')
    <...>
@manager.command
def runserver():
    <...>
    serve(flask_app, host='0.0.0.0', port='8080', threads=threads)
    <...>
```

After that, I created a variable that I named `ns` and it's a Flask object. This object has a
decorator `route` that exposes my functions to
 the web framework in a given URL pattern myapp:8080
  that has `"/check"` and `"/service"` as routes, GET and POST methods, respectively. 

I created one function for each method. The first is a message to know that the application is alive:

```python
# health GET endpoint
@ns.route('/check', methods=['GET'])
class ServerCheck(Resource):
    def get(self):
        now = datetime.now().strftime('%d/%b/%Y - %H:%M:%S.%f\n')
        return "OK!" + now.upper()
```

And the second the service the Service's main function:

```python
@ns.route('/service')
class DefaultApi(Resource):
    <...>
    @accepts(api=ns, schema=RequestSchema())
    def post(self):
        N, state = request.parsed_obj
        response = self.plants.top_n_plants(N=N, state=state)
        return response
```

The accepts decorator will check the input schema as defined in RequestSchema

```python
class RequestSchema(Schema):
    <...>
    N = fields.Integer(required=True)
    State = fields.String(required=False)
    <...>    
```

## Dockerfile
This is the Dockerfile of this project:

```dockerfile
FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED=1 APP_HOME=/micro/

RUN mkdir $APP_HOME && adduser --system --home /home/python python \
    && chown -R python $APP_HOME

WORKDIR $APP_HOME

ADD requirement*.txt $APP_HOME
ADD . $APP_HOME
RUN apt-get update \
    && pip install -r requirements.txt

USER python

CMD python3.7 ${APP_HOME}manage.py runserver
```

I choose a small operating system to build images faster and put the less prone to changes layers in the beginning.
In `requirements.txt` I put the necessary packages and its respective versions to execute my application.
The `CMD` command will be the one that runs when the container starts.


#Cloud Deployment (GCP)

To deploy this application in GKE I have created a CI/CD pipeline that builds the Docker images and executes 
some deployment files.
The deployment file is `cloudbuild.yaml`

## The `cloudbuild.yaml`

To build a CI/CD pipeline (not required but useful) I'll use CloudBuild, and the steps are
defined in `cloudbuild.yaml`. 

I'll describe each one of the steps of the `cloudbuild.yaml` of this project.

### Step 1: Pull an existing container image if it is already built

This step will pull an existing image from the Google Container Registry.

```yaml
  - name: 'gcr.io/cloud-builders/docker'
    entrypoint: 'bash'
    args:
      - '-c'
      - 'docker pull gcr.io/${_PROJECT_ID}/${_REPOSITORY}:latest || exit 0'
```


### Step 2:  Build the new application image using the previous one

If the first step didn't find an existing image, this command will create a new one, but if it did, this step
will use the existing image as a cache in this build.

```yaml
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/${_PROJECT_ID}/${_REPOSITORY}:latest'
      - '-t'
      - 'gcr.io/${_PROJECT_ID}/${_REPOSITORY}:${_VERSION}'
      - '--cache-from'
      - 'gcr.io/${_PROJECT_ID}/${_REPOSITORY}:latest'
      - '.'
      - '--network'
      - 'cloudbuild'
    timeout: 1200s
```
### Step 3: Push the image to Google Cloud Registry

The command will push the application's new image to the GCR with
both tags, `latest` and the `VERSION` set.

```yaml
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/${_PROJECT_ID}/${_REPOSITORY}'
```

### Step 4: Replace string variables in YAML file
I used `sed` command to replace values `PROJECT_ID`,`REPOSITORY`, `VERSION` and `SERVICE_NAME`  are default environment variables in Google Cloud Build.

```yaml
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        sed -i "s/PROJECT_ID/${_PROJECT_ID}/g" k8s/deployment.yaml && \
        sed -i "s/REPOSITORY/${_REPOSITORY}/g" k8s/deployment.yaml && \
        sed -i "s/VERSION/${_VERSION}/g" k8s/deployment.yaml && \
        sed -i "s/SERVICE_NAME/${_SERVICE_NAME}}/g" k8s/deployment.yaml
```

### Step 5: Deploy the application in Kubernetes

With this `kubectl`command you can deploy or update the model application in your Kubernetes cluster.
This command applies the two configuration files in `k8s/` folder. You only need to set two environment variables
to access your cluster: `CLOUDSDK_COMPUTE_ZONE` and `CLOUDSDK_CONTAINER_CLUSTER`.
```yaml
steps:
  # <...>
  - name: 'gcr.io/cloud-builders/kubectl'
    args:
      - 'apply'
      - '-f'
      - 'k8s/'
    env:
      - 'CLOUDSDK_COMPUTE_ZONE=southamerica-east1-b'
      - 'CLOUDSDK_CONTAINER_CLUSTER=aiq'
```

#### Create a Google Cloud Endpoint service

It is required to create an endpoint,  you just have to execute the command below.

```bash
# enter in endpoint folder, execute a script and return to project folder
cd endpoint && \
source endpoint-config.sh && \
cd ..
```
`endpoint-config.sh` basically get some parameters such as `SERVICE_NAME` and `SERVICE_IP` to 
execute commands that creates and enable the endpoint that exposes the service configured in `service.yaml`.


## Security: Create an API key

I have created an API Key to protect the Service.


## Run locally

It is possible to run the application locally, you just have to clone this repo, create a venv and install the requirements (`python3.7`), then
execute `pyhon manage.py runserver`, and it will run the application in your localhost.

To test it, you can make some request, let's try the ``/check`` endpoint with:

```
curl --request GET \
  --url http://localhost:8080/check
```

response:
```"OK!dd/mm/yyyy - H:M:S"```

``/service`` endpoint

```
curl --request POST \
  --url http://localhost:8080/service \
  --header 'Content-Type: application/json' \
  --data '{"N":2, "State":"AZ"}'
```

It will return the top 2 (N=2) plants of the "AZ" State

##Test in Cloud environment
**IMPORTANT:** API Key authentication required, please contact the project's developer for more information

```
curl --request POST \
  --url 'http://34.95.206.233/service?key=<API_KEY>' \
  --header 'Content-Type: application/json' \
  --data '{"N":200, "State":"AK"}'
```
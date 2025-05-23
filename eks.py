from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
import os
import time
from dotenv import load_dotenv
load_dotenv()

# Load configuration depending on environment
if os.getenv('KUBERNETES_SERVICE_HOST'):
    config.load_incluster_config()
else:
    config.load_kube_config()

# Configuration
IMAGE = os.getenv("FLASK_IMAGE")
PORT = int(os.getenv("FLASK_PORT", "5000"))
APP_NAME = "my-flask-app"
SERVICE_NAME = "my-flask-service"
NAMESPACE = "default"

# Create shared API client
api_client = client.ApiClient()

# Define deployment
deployment = client.V1Deployment(
    metadata=client.V1ObjectMeta(name=APP_NAME),
    spec=client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": APP_NAME}),
        template=client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": APP_NAME}),
            spec=client.V1PodSpec(containers=[
                client.V1Container(
                    name="flask-container",
                    image=IMAGE,
                    ports=[client.V1ContainerPort(container_port=PORT)]
                )
            ])
        )
    )
)

# Define service
service = client.V1Service(
    metadata=client.V1ObjectMeta(name=SERVICE_NAME),
    spec=client.V1ServiceSpec(
        selector={"app": APP_NAME},
        ports=[client.V1ServicePort(port=PORT, target_port=PORT)],
        type="LoadBalancer"
    )
)

# Apply Deployment
apps_v1 = client.AppsV1Api(api_client)
try:
    apps_v1.create_namespaced_deployment(namespace=NAMESPACE, body=deployment)
    print("Deployment created.")
except ApiException as e:
    if e.status == 409:
        apps_v1.replace_namespaced_deployment(name=APP_NAME, namespace=NAMESPACE, body=deployment)
        print("Deployment replaced.")
    else:
        raise

# Apply Service
core_v1 = client.CoreV1Api(api_client)
try:
    core_v1.create_namespaced_service(namespace=NAMESPACE, body=service)
    print("Service created.")
except ApiException as e:
    if e.status == 409:
        core_v1.patch_namespaced_service(name=SERVICE_NAME, namespace=NAMESPACE, body=service)
        print("Service patched.")
    else:
        raise

# Wait for LoadBalancer IP
print("Waiting for LoadBalancer EXTERNAL-IP...")
for _ in range(20):
    svc = core_v1.read_namespaced_service(name=SERVICE_NAME, namespace=NAMESPACE)
    ingress = svc.status.load_balancer.ingress
    if ingress:
        lb_host = ingress[0].hostname or ingress[0].ip
        print(f" Your app is available at: http://{lb_host}:{PORT}/")
        break
    time.sleep(10)
else:
    print("LoadBalancer EXTERNAL-IP not ready after 100 seconds.")

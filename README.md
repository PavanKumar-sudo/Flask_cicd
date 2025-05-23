# Flask System Monitoring Dashboard with AWS EKS & CI/CD
## 📋 Prerequisites

To run and deploy this project, you must have the following tools installed and configured on your system:

1. **AWS CLI**
   - Used to authenticate and interact with AWS services (EKS, IAM, S3, etc.)
   - 🔗 [Download & Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

2. **Kubectl**
   - Kubernetes command-line tool for managing clusters and resources.
   - 🔗 [Install Kubectl](https://kubernetes.io/docs/tasks/tools/)

3. **eksctl**
   - A CLI tool to create and manage EKS clusters with ease.
   - 🔗 [Install eksctl](https://eksctl.io/introduction/#installation)

4. **Docker**
   - Used for building and running application containers.
   - 🔗 [Install Docker](https://docs.docker.com/get-docker/)

5. **GitHub CLI (Optional)**
   - For interacting with GitHub repositories and automating pull/push from CLI.
   - 🔗 [Install GitHub CLI](https://cli.github.com/)

6. **AWS Access Credentials**
   - Ensure your `~/.aws/credentials` file is properly configured with:
     ```ini
     [default]
     aws_access_key_id = YOUR_ACCESS_KEY
     aws_secret_access_key = YOUR_SECRET_KEY
     region = us-east-1
     ```
   - 🔗 [How to configure AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
7. clone my repo and start build the docker image
```bash
git clone <git-clone-link>
docker build -t $DOCKER_IMAGE:latest
```
## Project explanation:
#  Flask System Monitoring Dashboard

This project is a lightweight system monitoring web application built using Flask and Plotly.js that provides real-time visualization of CPU and memory usage on the host machine. At its core, the backend logic - app.py uses the psutil library to fetch the current CPU and memory usage percentages of the system on which the app is running. When the usage of either metric exceeds 80%, the application dynamically triggers a warning message on the dashboard indicating high resource consumption and the need to potentially scale up resources.

The frontend is rendered through a Flask Jinja2 template - index.html and displays two beautifully styled interactive gauge charts using Plotly — one each for CPU and memory usage. The gauges are color-coded to reflect normal, warning, and critical thresholds, making it visually intuitive to monitor system health. If CPU or memory exceeds the 50% threshold, the dashboard alerts the user in red with a clear message. And also we will get the alert box in UI. The web app is responsive, and the gauges are centrally aligned for clarity and ease of use.

Note: It calculate the CPU and memory of System where you running for example if you running on your local it calculates your local system if running on Kuberentes it calculate only that pod CPU and memory not entire pod

First, I check my app is running on the local machine on the port 5000 by doing this step.

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Run the Flask app
python3 app.py
#5 to check the cpu usage and memory usage run in like 4-5 broswers or cli
python3 -c "while True: pass"
python3 -c "a=[]; [a.append(' ' * 10**6) for _ in range(500)]"
```
Output:
 
 
 ![image](https://github.com/user-attachments/assets/ca9b780f-fdb0-47c5-b77b-f36e717d224f)
 ![image](https://github.com/user-attachments/assets/e8ea466d-d861-4271-9dd6-06b33d7abf91)
 ![image](https://github.com/user-attachments/assets/5b1df8a1-d4c1-49f4-aa03-11da2cb6a2f4)



DockerFile:

This project uses a multi-stage Dockerfile to build and package the Flask-based system monitoring application in a clean and efficient way. In the first stage, a full Python 3.11 image (python:3.11-buster) is used to install all required system-level dependencies and Python packages listed in requirements.txt. These dependencies are installed into a custom directory (/install) to keep them isolated and portable.

In the second stage, a lightweight runtime image (python:3.11-slim) is used to assemble the final container. Only the built application and its dependencies are copied over, significantly reducing the image size and improving security. The container exposes port 5000 and starts the Flask app using flask run. This setup ensures a clean separation between build and runtime environments, making the image optimized for production deployment on platforms like Docker, Amazon ECR, and Kubernetes (EKS). I used the mutli stage docker image to reduce the my docker  image size.
 

To Test my docker image is working I used below commands in my local environment.
```bash
# Build the Docker image
docker build -t flask-system-monitor .

# Run the container locally and map it to port 5000
docker run -p 5000:5000 flask-system-monitor
```
Output:
 ![image](https://github.com/user-attachments/assets/1b582cb6-f81a-43c3-a2b3-f3fd7296b2bc)
![image](https://github.com/user-attachments/assets/bdefd676-8643-43f5-a9fc-bb1cc2b706d9)
![image](https://github.com/user-attachments/assets/cfd254b2-c734-4b92-86d3-53bef5152e64)

 
## pushing the my docker image into ecr.

The ecr.py script automates the entire process of working with Amazon ECR (Elastic Container Registry). It first takes a repository name as a command-line argument and attempts to create a new ECR repository in the us-east-1 region using the AWS credentials provided via environment variables. If the repository already exists, it gracefully retrieves its URI. The script then builds a local Docker image from the current directory using that repository name and tags it with the correct ECR URI. This ensures the image is properly formatted and ready to be uploaded to AWS.

Once the image is built and tagged, the script logs into Amazon ECR using the AWS CLI, and finally pushes the Docker image to the specified ECR repository. This end-to-end workflow removes the need to run Docker and AWS commands manually, making it ideal for local development and CI/CD automation. This script supports both local usage (with AWS CLI configured) and cloud environments (using environment variables), making it flexible and deployment-ready.

```bash
# it will ask your aws cli access key and secret key and which region you what to create and output
aws configure --profile profile_name
# Run this from your project directory
python3 ecr.py dockerimage_name
```
Output:

![image](https://github.com/user-attachments/assets/80452f43-9eab-4887-b4dd-d45d73016686)
![image](https://github.com/user-attachments/assets/ed4266f7-eadc-49d7-9d4c-1c082cceb09d)
 
 
### EKS Cluster Setup and Application Deployment

To create an Amazon EKS cluster, there are multiple approaches available. Below are the most common and effective methods:

1. **Manual Setup (Console-based):** [YouTube Tutorial](https://www.youtube.com/watch?v=N4np9l1ILGs)  
2. **Infrastructure as Code (IaC) with Terraform:** [YouTube Tutorial](https://www.youtube.com/watch?v=_BTpd2oYafM)  
3. **Automation using `eksctl` CLI:** (Recommended for quick setups)

To create and connect to your EKS cluster using `eksctl`, follow these steps:

```bash
# Create an EKS cluster with 2 t3.medium worker nodes and autoscaling
eksctl create cluster \
  --name cd-cluster \                     
  --region us-east-1 \                    
  --node-type t3.medium \                 
  --nodes 2 \                             
  --nodes-min 1 \                         
  --nodes-max 4 \                         
  --managed 
  --vpc-nat-mode Disable                  

# Configure kubectl to connect to your EKS cluster
aws eks update-kubeconfig --region us-east-1 --name cd-cluster

# Verify if the worker nodes are ready
kubectl get nodes
```
output:
![image](https://github.com/user-attachments/assets/9349744a-d09a-4956-afbb-865e6c8ab21a)
![image](https://github.com/user-attachments/assets/0154d39f-d859-49c0-9c49-8b19fc7f624e)
![image](https://github.com/user-attachments/assets/fa516647-f94e-4fbe-ba47-4fa310ae5dd2)

 
Created node group:
 
 
Once the cluster and nodes are ready, you can deploy your application using the eks.py script. This script automates the deployment of your Dockerized Flask application to EKS using the Kubernetes Python client. It loads your kubeconfig (or in-cluster config), reads environment variables for the image and port, and creates a Deployment object that runs your Flask app inside a Kubernetes pod.
The script also creates a LoadBalancer-type Kubernetes Service, which exposes your app externally. If the deployment or service already exists, it replaces or patches them. Finally, it polls the service until an external IP is assigned and prints the full public URL where the app can be accessed. This script is typically used as the final step in a CI/CD pipeline after building and pushing the Docker image to Amazon ECR.

First I run in my local in order to run in my local you need to install all requirement module so I created a virtual python environment and run my eks.py file. So to do that I run this all commands.

```bash
# Create a virtual environment in the local project directory
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install all required Python packages listed in requirements.txt
pip install -r requirements.txt

# Run the deployment script
python eks.py
```
Then verify your application is deployed and the Kubernetes objects are functioning:
```bash
kubectl get nodes                      # Check node status
kubectl get deployment -n default     # Check if the Flask deployment exists
kubectl get svc -n default -w         # Watch for the LoadBalancer EXTERNAL-IP
kubectl get pods -n default -w        # Watch your Flask pod status
```
 output:
 ![image](https://github.com/user-attachments/assets/7c1e7532-5d23-4525-8766-274a83f4b4ae)

 
To delete all the deployment and pod and service.
```bash
# Delete deployment
kubectl delete deployment my-flask-app -n default

# Delete service
kubectl delete service my-flask-service -n default

# Optionally, delete pod directly (but it'll be removed with deployment)
kubectl delete pod --all -n default
```
### Setting up CICD pipeline for above project
In this CI/CD pipeline, I automated the process of testing, building, and deploying a Python Flask application to Amazon EKS using GitHub Actions. On every push to the main branch, the workflow sets up the Python environment, installs dependencies from requirements.txt, and runs unit tests. It then authenticates with AWS using GitHub Secrets, builds a Docker image of the Flask app, and pushes it to Amazon ECR. Finally, it updates the kubeconfig to connect to the EKS cluster and runs a custom eks.py script to deploy the app by creating or updating a Kubernetes Deployment and LoadBalancer Service. The pipeline also outputs the external URL of the deployed app once available.
Secret configure in github:
Secret Name	Description
AWS_ACCESS_KEY_ID	Your AWS access key
AWS_SECRET_ACCESS_KEY	Your AWS secret key
AWS_REGION	AWS region (e.g., us-east-1)
ECR_REPOSITORY	Full ECR URI (e.g., 1234.dkr.ecr...)
EKS_CLUSTER_NAME	Name of your EKS cluster

 output:
 ![image](https://github.com/user-attachments/assets/bf5bd417-defa-4776-be00-8438a039c52d)
 ![image](https://github.com/user-attachments/assets/93c6dcef-7c4d-409f-8909-11781b01d8af)
 

## Cleanup
Make sure need to run this commands to clean up everything so that it will cost you
```bash
# it will delete your eks cluster
eksctl delete cluster --name my-first-eks-cluster --region us-east-1
#it will delete your ecr repository
aws ecr delete-repository --repository-name <your-repo-name> --force --region <your-region>
```
## 🔮 Future Considerations

To enhance scalability, security, and production-readiness, the following improvements are planned:

1. **Cluster-Wide Monitoring Support**  
   Extend the application to collect metrics from multiple pods or nodes using Prometheus and Grafana for full Kubernetes visibility.

2. **Persistent Metrics Storage**  
   Integrate a time-series database like InfluxDB or Prometheus TSDB to store and analyze historical CPU/memory trends.

3. **Authentication and Access Control**  
   Implement user login and role-based access using OAuth2, JWT, or AWS Cognito to secure dashboard access.

4. **Automated Alerts and Notifications**  
   Add support for email, Slack, or AWS SNS alerts when resource thresholds are breached, enabling proactive incident response.

---



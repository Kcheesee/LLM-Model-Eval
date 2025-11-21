# Kubernetes Command Cheatsheet

## What You Just Learned

### Cluster Management
```bash
minikube start              # Start your local K8s cluster
minikube stop               # Stop the cluster
minikube delete             # Delete the cluster
minikube dashboard          # Open K8s web UI
kubectl cluster-info        # Show cluster info
```

### Pod Operations
```bash
kubectl get pods                    # List all pods
kubectl get pods -w                 # Watch pods in real-time
kubectl describe pod <pod-name>     # Detailed pod info
kubectl logs <pod-name>             # View pod logs
kubectl logs -f <pod-name>          # Stream logs (like tail -f)
kubectl exec <pod-name> -- <cmd>    # Run command in pod
kubectl exec -it <pod-name> -- bash # Interactive shell in pod
kubectl delete pod <pod-name>       # Delete a pod
```

### Apply/Deploy Resources
```bash
kubectl apply -f <file.yaml>        # Create/update resources from YAML
kubectl delete -f <file.yaml>       # Delete resources from YAML
```

### Port Forwarding (for testing)
```bash
kubectl port-forward <pod-name> <local-port>:<pod-port>
# Example: kubectl port-forward hello-nginx 8080:80
```

### Other Useful Commands
```bash
kubectl get all                     # List all resources
kubectl get nodes                   # List cluster nodes
kubectl get namespaces              # List namespaces (like folders for resources)
kubectl config view                 # View kubectl configuration
```

## What's Next

You've mastered:
- Starting a local K8s cluster
- Deploying your first pod
- Viewing logs and describing resources
- Executing commands in containers
- Port forwarding for testing

Next session: We'll deploy TrustChain!

# game-server-glutamate
Game Server Glutamate is a game-servers' traffic switch. It is a process that multiplex UDP traffic to its target game-servers – wherever it finds a game server receptor to dock with.

In this project, we demonstrate how to increase dedicated game servers availability by applying advanced scheduling in Kubernetes and an NGINX-based load balancer. Our core motivation for this project comes from the unfolded need in the gaming industry to reduce compute costs to accommodate emerging gaming patterns such as free-to-play. 

AWS Spot Instances offers a viable compute offering for casual mobile game servers because of its 2-minute interruption notification and the low interruption rates observed. More info about determining the chance of interruption is available in [Spot Instance Advisor](https://aws.amazon.com/ec2/spot/instance-advisor/). In such cases, customers can save up to 90% of their compute cost. 

## License Summary
This sample code is made available under a modified MIT license. See the LICENSE file.

## Introduction
We present an option for hardcore games dedicated game server workloads that unlikely interruption is undesirable. We use a naive approach to reduce the already negligible chance for an interruption by doubling the amount of Spot compute resources in the elastic k8s worker nodes (ASG-based). We partition the worker nodes to two main instance groups and enforce a scheduling policy that will prevent two target game servers to run on the same spot instance. By that, we reduce the likelihood for spot interruption by 50% from the already low probability.  

The project includes the following main components:
* The game server [mockup-udp-server](https://github.com/aws-samples/game-server-glutamate/tree/master/mockup-udp-server-image). This is a simple UDP socket server that accepts a delta of a game state from connected players and multicast back to its players the updated state based on pseudo computation. It is a single threaded server, and its goal is to prove the viability of UDP-based load balancing in dedicated game-servers. The model presented herein is not limited to this implementation. It is deployed as a single-container Kubernetes pod that uses `hostNetwork: true` for network optimization. 
*  The load-balancer [udp-lb](https://github.com/aws-samples/game-server-glutamate/tree/master/udp-lb-image). This is a containerized NGINX server loaded with the `stream` [module](https://github.com/aws-samples/game-server-glutamate/blob/master/udp-lb-image/nginx.conf.template). The load balance `upstream`  set is configured upon init based on the dedicate game-server state that is stored in DynamoDB table `game-server-status-by-endpoint`. Availiable load balancer instances are also stored in a DynamoDB table `lb-status-by-endpoint` to be used by core game services such as matchmaking service. 
* SQS queue that captures the initialization and termination of game servers and load balancers instances deployed in the Kuberentes cluster. 
* DynamoDB tables that persist the state of the cluster w.r.t. game servers and load balancer inventory. 
* Lambda-based API [game-server-inventory-api-lambda](https://github.com/aws-samples/game-server-glutamate/tree/master/game-server-inventory-api-lambda) that serves the game servers and load balancers for an updated list of resources available. The API currently supports `/get-available-gs` needed for the load balancer to set its upstream target game servers. It also supports `/set-gs-busy/{endpoint}` for labeling already claimed game servers from the available game servers inventory. 
* Lambda-based function [game-server-status-poller-lambda](https://github.com/aws-samples/game-server-glutamate/tree/master/game-server-status-poller-lambda) that triggered by the SQS queue and populates the DynamoDB tables. 

## The Data Flow
![alt text](https://github.com/aws-samples/game-server-glutamate/blob/master/pics/game-server-glutamate.png)

## Scheduling Mechanism
The goal is to reduce the chance for two game-servers that serves the same load-balancer game endpoint will be interrupted at once. Therefore, there is a need to prevent the scheduling of the same game servers, `mockup-UDP-server` in this sample. In general, this project uses [advanced-scheduling-in-kubernetes](https://kubernetes.io/blog/2017/03/advanced-scheduling-in-kubernetes/) where Pod Affinity/Anti-Affinity policy is being applied. 

This project defines two soft labels `mockup-grp1` and `mockup-grp2` under the `podAffinity` section as follow:
```
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: "app"
                    operator: In
                    values:
                      - mockup-grp1
              topologyKey: "kubernetes.io/hostname"
```
The `requiredDuringSchedulingIgnoredDuringExecution` will indicate the scheduler that the rules below must be met upon pod scheduling. The rule says that pods that carry the value of `key: "app"` `mockup-grp1`  will not be scheduled on the same node as pods with `key: "app"` `mockup-grp2` due to  `topologyKey: "kubernetes.io/hostname"`

When a load balancer pod (`udp-lb`) is scheduled, it will query the `game-server-inventory-api` endpoint that query for two game-server pods that run on different nodes. If this request will not be fulfilled, the load balancer pod will enter a crash loop until two available game-servers are ready. 

## The Setup Process 
* Build an EKS cluster using [EKS Getting started guide](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html)
* Configure and allocate Spot-based ASG using [spotable-game-server](https://github.com/aws-samples/spotable-game-server)
* Create two DynamoDB tables as follow:

`gs-status-by-endpoint` and `lb-status-by-endpoint` with status-group-index, `status` is key and `group` is sort key
* Create a regular SQS queue `serverstatus`
* Deploy the `game-server-status-poller` lambda function under [game-server-status-poller-lambda](https://github.com/yahavb/game-server-glutamate/tree/master/game-server-status-poller-lambda)
* Deploy the `game-server-inventory-api` lambda function and API gateway using Chalice. 
* Build the images of both [mockup-udp-server-image](https://github.com/yahavb/game-server-glutamate/tree/master/mockup-udp-server-image) and [udp-lb-image](https://github.com/aws-samples/game-server-glutamate/tree/master/udp-lb-image) using the `buid.sh` script 
* Deploy the first group of game servers k8s deployment using the spec [mockup-udp-server-grp1-deploy.yml](https://github.com/aws-samples/game-server-glutamate/blob/master/specs/mockup-udp-server-grp1-deploy.yml)
* Deploy the second group of game servers k8s deployment using the spec [mockup-udp-server-grp1-deploy.yml](https://github.com/aws-samples/game-server-glutamate/blob/master/specs/mockup-udp-server-grp1-deploy.yml)
* Observe both tables `gs-status-by-endpoint` and `lb-status-by-endpoint` for the values alloacted by the scheduler.
* Scale the game servers deployments and load balancer deployments and observe the value assigned. 
* Deploy app clients that will connects one of the load balancers public endpoints (one of the values from `lb-status-by-endpoint`)
* export the `SERVER_ENDPOINT` with the LB value and execute [app.py](https://github.com/aws-samples/game-server-glutamate/blob/master/game-client-image/app.py)

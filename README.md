# learning_docker

## Source
[Docker Essentials: A Developer Introduction](https://cognitiveclass.ai/courses/docker-essentials/)

## Playground
[Play with Docker](https://labs.play-with-docker.com)
> needs docker hub account: https://hub.docker.com/
  
# L1 - Run your first container

## What are containers

- They are nothing more than a process or group of processes that are running in isolation. 
- They run on a shared kernel
- the isolation is provided by __linux namespaces__
    - each container has it's own set of "namespaces":
        - __PID__ - process IDs
        - __USER__ - user and group IDs
        - __UTS__ - hostname and domain name
        - __NS__ - mount points
        - __NET__ - network devices, stacks, ports
        - __IPC__ - inter-process communications, message queues
- __cgroups__ (another linux feature) controls limits and monitoring or resources

### VMs vs Container

![](VM-vs-Container.jpg)

## Run a container

Image vs Container  

An image is the blueprint for spinning up containers. An image is a TAR of a file system, and a container is a file system plus a set of processes running in isolation.

```shell
docker container run -t ubuntu top
```
- `docker container run` run a container with Ubuntu image
- run `top` command, in that container
- `-t` flag allocates a pseudo-TTY (so that `top` command will work correctly)
- `docker run` command first starts a `docker pull` command to download the Ubuntu image onto your host, and then it will start the container
- when done, stop it with `<ctrl>+c`

Inspect the container from a different process:
- `docker container exe` - allows you to enter a running container's namespaces with a new process
- `docker container ls` - to list current containers
- after you get the container ID, you can use it like this: `docker container exec -it [container ID] bash`
- `-it` - gives interactive (open STDIN) TTY console
- `bash` - runs bash in the new console
- `ps -ef` - to check the running processes in the given Ubuntu container (you can run it outside, and see the difference)

## Run multiple containers

[Docker Hub](https://hub.docker.com/) is the public central registry for Docker images. Find one that you would like to use there. 

> Try to avoid using unverified content from Docker, as some images might contain security vulnerabilities or even malicious software.

Next, we will use NGINX web server and MongoDB:

1. Run an NGINX server

```shell
docker container run --detach --publish 8080:80 --name nginx nginx
```
- `--detach` - run the container in background
- `--publish` - publish port 80 in the container by using port 8080 on your host
- `--name` - every container has a name. If you don't give one, Docker makes one up (funny ones even)
- `nginx` - (last one) is the same as `nginx:latest` (image_name:version_tag)

2. Run a MongoDB server

```shell
docker container run --detach --publish 8081:27017 --name mongo mongo:3.4
```
- `mongo:3.4` - instead of using the default __latest__ tag, we use specific __3.4__ version

Check you containers:
```shell
docker container ls
```
Output should be similar to:
```shell
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                     NAMES
e4915cc89e5c        mongo:3.4           "docker-entrypoint.s…"   32 seconds ago      Up 29 seconds       0.0.0.0:8081->27017/tcp   mongo
5742570ace3d        nginx               "nginx -g 'daemon of…"   4 minutes ago       Up 4 minutes        0.0.0.0:8080->80/tcp      nginx
```

## Remove the containers

Run this command for each container that you want to stop
```shell
docker container stop [container id]
```
You can reference them by the name or container ID. If you use the ID, you only need to enter enough digits so that the ID is unique (usually 3 will suffice).
```shell
docker container stop e49 574
```

Remove the stopped containers

`docker container list -a` - to list all containers

```shell
docker system prune
```
This command will remove any stopped containers, unused volumes and networks, and dangling images.


# L2 - Add CI/CD value with Docker images


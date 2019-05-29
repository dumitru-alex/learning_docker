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

## Create a sample Python app

- it can be done with any other programming language (it will change the requirements going forward).  
- we create this sample python app locally, so we can dockerize it later.
- see [Sample python app](app.py).
- Pre-reqs: python 3, Flask (not needed if you don't want to test the app locally)

## Create and build the Docker image

- see [Dockerfile](Dockerfile) built for this example
- a Dockerfile lists the instructions needed to build a Docker image
- explanation for the content of our Dockerfile:
    - `FROM python:3.6.1-alpine`
        - starting point for our Dockerfile
        - every Dockerfile typically starts with a `FROM` line that is the starting image to build your layers on top of
        - `3.6.1-alpine` is the tag for this Python image. Check all available tags at [Python Image](https://hub.docker.com/_/python/). If no tag is specified, then `latest` will be used.
        - if you want more customization power over your image, you can start at a higher level, by taking the Dockerimage of python, which in this case starts with a `FROM alpine` statement, and alter the subsequent commands yourself as needed.
    - `RUN pip install flask`
        - the `RUN` command executes commands needed to set up your image for your application, such as installing packages, editing files, or changing file permissions.
        - in this case, we are installing flask.
        - the `RUN` commands are executed at build time and are added to the layers of your image
    - `CMD ["python","app.py"]`
        - `CMD` is the command that is executed when you start a container
        - here we are using `CMD` to run our Python application
        - there can be only one `CMD` per Dockerfile! if you specify more, then the last one will take effect
        - we can use the official Python image directly to run Python scripts withouts installing Python on our machine. However, in our case, we want to create a custom image that includes our source along side the needed requirements, so that we can ship it to other environments directly
    - `COPY app.py /app.py`
        - copies the `app.py` file from the local directory (place where you will run `docker image build` command) into a new layer of the image
        - this instruction is the last line in Dockerfile. Layers that change frequently, such as copying source code into the image, should be placed near the bottom of the file to take full advantage of the Docker layer cache. This allows us to avoid rebuilding layers that could otherwise be cached. For instance, if there would be a change in the `FROM` instruction, it would invalidate the cache for all subsequent layers of this image
        - it seems counter-intuitive to put this line after the `CMD ["python","app.py"]` line. The CMD line is executed only when the container is started, so you won't get a _file not found_ error here
- for a full list of commands available to build a Docker Image, see [doc](https://docs.docker.com/engine/reference/builder/).

To build our image we run the following command:
```
docker image build -t python-hello-world .
```
Check the image newly created, and run it
```
docker image ls
docker run -p 5001:5000 -d python-hello-world
```
Now navigate to http://localhost:5001/. You should shee "Hello World!" in your browser window.  
If needed, you can check the log of your app by using:
```
docker container logs [container_id]
```

The Dockerfile is used to create reproducible builds for your application. A common workflow is to have your CI/CD automation run docker image build as part of its build process. After images are built, they will be sent to a central registry where they can be accessed by all environments (such as a test environment) that need to run instances of that application.

## Push to a central registry

- pre-req: account on https://hub.docker.com/

1. Log in to the Docker registry account:
```
docker login
```
2. Tag the image with your username:
- the naming convention is to tag your image with [dockerhub username][image name]
```
docker tag python-hello-world [dockerhub username]/python-hello-world
```
3. Push the image to the Docker Hub registry:
```
docker push dumitrualex/python-hello-world 
```

You can now check it on Docker repository:  
https://cloud.docker.com/u/dumitrualex/repository/list  (personal view while logged in as owner)
https://hub.docker.com/r/dumitrualex/python-hello-world (public view)
https://hub.docker.com/u/dumitrualex (public list with all my repositories)

Now that the image is on Docker Hub, other developers and operators can use the `docker pull` command to deploy our image to other environments.

> __Remember__: Docker images contain all the dependencies that they need to run an application within the image. This is useful because you no longer need to worry about environment drift (version differences) when you rely on dependencies that are installed on every environment you deploy to. You also don't need to follow more steps to provision these environments. Just one step: install docker, and that's it.

## Deploy a change

Let's say we have made an update to our application source file.
- change text from "Hello World" to "Hello Everyone".

Now we need to rebuild our Docker image. We are using the same command:
```
docker image build -t python-hello-world .
```
- but now we notice the cache in action. Notice the "Using cache" for Steps 1 - 3. These layers of the Docker image have already been built, and the docker image build command will use these layers from the cache instead of rebuilding them.

Same goes for `push`
```
docker push dumitrualex/python-hello-world 
```
- there is a caching mechanism in place for pushing layers too. Docker Hub already has all but one of the layers from an earlier push, so it only pushes the one layer that has changed. For the others, it displays "Layer already exists".

When you change a layer, every layer built on top of that will have to be rebuilt. Each line in a Dockerfile builds a new layer that is built on the layer created from the lines before it. This is why the order of the lines in your Dockerfile is important. You optimized your Dockerfile so that the layer that is most likely to change (`COPY app.py /app.py`) is the last line of the Dockerfile. Generally for an application, your code changes at the most frequent rate. This optimization is particularly important for CI/CD processes where you want your automation to run as fast as possible.

## Understand image layers

One of the important design properties of Docker is its use of the union file system.

Consider the Dockerfile that you created before:
```docker
FROM python:3.6.1-alpine
RUN pip install flask
CMD ["python","app.py"]
COPY app.py /app.py
```

Each of these lines is a layer. Each layer contains only the delta, or changes from the layers before it. To put these layers together into a single running container, Docker uses the union file system to overlay layers transparently into a single view.

Each layer of the image is read-only except for the top layer, which is created for the container. The read/write container layer implements "copy-on-write," which means that files that are stored in lower image layers are pulled up to the read/write container layer only when edits are being made to those files. Those changes are then stored in the container layer.

The "copy-on-write" function is very fast and in almost all cases, does not have a noticeable effect on performance. You can inspect which files have been pulled up to the container level with the `docker diff` command. For more information, see the command-line reference on the [docker diff](https://docs.docker.com/engine/reference/commandline/diff/) command.

![](docker_image_layer.png)

Because image layers are read-only, they can be shared by images and by running containers. For example, creating a new Python application with its own Dockerfile with similar base layers will share all the layers that it had in common with the first Python application.

```docker
FROM python:3.6.1-alpine
RUN pip install flask
CMD ["python","app2.py"]
COPY app2.py /app2.py
```

![](docker_image_layer2.png)

You can also see the sharing of layers when you start multiple containers from the same image. Because the containers use the same read-only layers, you can imagine that starting containers is very fast and has a very low footprint on the host.

You might notice that there are duplicate lines in this Dockerfile and the Dockerfile that we created earlier. Although this is a trivial example, we can pull common lines of both Dockerfiles into a base Dockerfile, which we can then point to with each of your child Dockerfiles by using the FROM command.

Image layering enables the docker caching mechanism for builds and pushes. For example, the output for our last docker push shows that some of the layers of our image already exist on the Docker Hub.

To look more closely at layers, you can use:
```
docker image history [image id]
```
- Each line represents a layer of the image
- notice that the top lines match to the Dockerfile that we created, and the lines below are pulled from the parent Python image. 
- don't worry about the `<missing>` tags. These are still normal layers; they have just not been given an ID by the Docker system.

## Remove containers

- Get a list of running containers with `docker container ls`
- Stop specific one with `docker container stop [container id]`
- Remove stopped containers with `docker system prune`



# Server

## Running the code

Building the Docker images:

```
$ ./run.sh docker-build
```

Without Docker:

```
$ ./run.sh setup
```

### Running in default mode
Docker:
```
$ ./run.sh docker -d
```
Without Docker:
```
$ ./run.sh -d
```

### Running in production mode
Docker:
```
$ ./run.sh docker PROD
```
Without Docker:
```
$ ./run.sh PROD
```

### Running with custom configurations
Docker:
```
$ ./run.sh docker MY_CONFIG
```
Without Docker:
```
$ ./run.sh MY_CONFIG
```
# jauth
- ***Installable user authorization/authentication service*** even contains third party users like Google, Facebook, Apple ...

## Pre-requisites
- docker >= 19.03.8
- docker-compose >= 1.25.5
- python >= 3.7

## Quick start (on local)
```
$ docker-compose -f local-docker-compose.yml up -d
```

## API server

### Run server
```
$ export ENV=dev
$ export API_SERVER__JWT_SECRET={...JWT SECRET....}
$ export API_SERVER__MYSQL__HOST={...}
$ export API_SERVER__MYSQL__USER={...}
$ export API_SERVER__MYSQL__PASSWORD={...}
$ export API_SERVER__REDIS__HOST={...}
$ export API_SERVER__REDIS__PASSWORD={...}
$ python3 -m apiserver
```

### Run worker with docker-compose in local
```
$ docker-compose -f local-docker-compose.yml up -d api-server
```

## Project structure
```
/
  /apiserver
```
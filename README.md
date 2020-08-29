<div align="center">
  <br/>
  <img src="./docs/image/jauth-logo.png" width="200"/>
  <br/>
  <br/>
  <p>
    Installable user authorization / authentication service  <br/>
    even contains third party users like Google, Facebook, Apple ...  
  </p>
  <p>
    <a href="https://github.com/pjongy/jauth/blob/master/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-blue.svg"/>
    </a>
  </p>
</div>


---

## Quick start (on local)

### Pre-requisites
- docker >= 19.03.8
- docker-compose >= 1.25.5

```
$ docker-compose -f local-docker-compose.yml up -d
```

## Project structure
```
/
  /jauth
```


## Pre-requisite
- Run mysql server and create database
    ```
    $ docker run -d -e  MYSQL_ROOT_PASSWORD={..mysql password..} -p 3306:3306 mysql
    ```
- Run Redis server
    ```
    $ docker run -d -p 6379:6379 redis
    ```

## Build
```
$ docker build . -f ./jauth/Dockerfile
```

## Start
```
$ docker run \
 -e ENV=dev \
 -e API_SERVER__JWT_SECRET=jwt_secret \
 -e API_SERVER__MYSQL__HOST={..mysql host..} \
 -e API_SERVER__MYSQL__USER={..mysql user..} \
 -e API_SERVER__MYSQL__DATABASE={..mysql database name..} \
 -e API_SERVER__MYSQL__PASSWORD={..mysql password..} \
 -e API_SERVER__REDIS__HOST={..redis host..} \
 -e API_SERVER__REDIS__PASSWORD={..redis password..} \
 -e API_SERVER__INTERNAL_API_KEYS={..comma separated internal access keys..} \
 -e WORKER_COUNT=1 \
 -p 80:8080\
 pjongy/jauth
```
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
[API-SPEC](./jauth/README.md)

# Usage

## Quick start (on local)

```
$ docker-compose -f local-docker-compose.yml up -d
```

## Manually start

- Run mysql server and create database
  ```
  $ docker run -d -e  MYSQL_ROOT_PASSWORD={..mysql password..} -p 3306:3306 mysql
  ```
- Run
  ```
  $ docker run \
   -e ENV=dev \
   -e API_SERVER__JWT_SECRET=jwt_secret \
   -e API_SERVER__MYSQL__HOST={..mysql host..} \
   -e API_SERVER__MYSQL__USER={..mysql user..} \
   -e API_SERVER__MYSQL__DATABASE={..mysql database name..} \
   -e API_SERVER__MYSQL__PASSWORD={..mysql password..} \
   -e API_SERVER__INTERNAL_API_KEYS={..comma separated internal access keys..} \
   -e API_SERVER__EVENT_CALLBACK_URLS={..comma separated string bar separated url sets..} \
   -e WORKER_COUNT=1 \
   -p 80:8080\
   pjongy/jauth
  ```

# Develop

## Build

```
$ docker build . -f ./jauth/Dockerfile
```

## Test

```
$ docker-compose -f test-docker-compose.yml up -d --build jauth-tester
```

## Project structure

```
/
  /jauth  # API server implementation path
  /endpoint_test  # Dependency manipulated API server for testing and API endpoint level tester
```

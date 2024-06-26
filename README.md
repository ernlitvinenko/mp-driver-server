# MP Driver Backend

## Production Usage

### Requirements
1. Docker and docker-compose installed
2. WSL 2 (Windows Subsystem for Linux) installed (if you are on Windows)
3. Git installed

### Installation
1. From source code.
2. Via docker-compose.

#### Git
1. Clone this repository
```bash
git clone git@git.elitvinenko.tech:ernestlitvinenko/mp_driver_server.git
```

2. Change directory to the repository
```bash
cd mp_driver_server
```
3. Run the following command to start the server
```bash
docker-compose build && docker-compose up -d
```
4. The server should be started on `http://localhost:8000`


#### Docker-compose
1. Create a new directory for the project
```bash
mkdir mp_driver_server
```
2. Change directory to the new directory
```bash
cd mp_driver_server
```
3. Create a new file called `docker-compose.yml` and paste the following content
```yaml


HOST=a.thomsen-it.dk
DIR=deployment
USER=agpbruger
PORT=22022

FILES=caddy mongo observer webrtc controller docker-compose.yaml

all:
	@echo "Options include:"
	@echo "  upload  - Uploads the local configuration files"
	@echo "  start   - Starts the services from docker-compose"
	@echo "  stop    - Stops the services from docker-compose"
	@echo "  restart - Stops and starts the services."
	@echo "  status  - Get the status of the services"
	@echo "  pull    - Pulls the latest images of the services"
	@echo "  logs    - Get the latest 20 logs and follows the next logs"
	@echo "  ssh     - Gets an ssh shell on the server"
	

ssh:
	@echo "> Connecting to $(HOST)"
	ssh -p $(PORT) $(USER)@$(HOST)

upload:
	@echo "> Uploading files to $(HOST)"
	scp -P $(PORT) -r $(FILES) $(USER)@$(HOST):$(DIR)

start:
	@echo "> Starting the services on $(HOST)"
	ssh -p $(PORT) $(USER)@$(HOST) "docker-compose -f $(DIR)/docker-compose.yaml up -d --remove-orphans"

stop:
	@echo "> Stopping the services on $(HOST)"
	ssh -p $(PORT) $(USER)@$(HOST) "docker-compose -f $(DIR)/docker-compose.yaml down"

restart: stop start

status:
	@echo "> Status of the services on $(HOST)"
	ssh -p $(PORT) $(USER)@$(HOST) "docker-compose -f $(DIR)/docker-compose.yaml ps"

pull:
	@echo "> Pulling latest images $(HOST)"
	ssh -p $(PORT) $(USER)@$(HOST) "docker-compose -f $(DIR)/docker-compose.yaml pull"

logs:
	@echo "> getting logs from $(HOST)"
	ssh -p $(PORT) $(USER)@$(HOST) "docker-compose -f $(DIR)/docker-compose.yaml logs -f --tail 20"
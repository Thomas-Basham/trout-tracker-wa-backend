REGISTRY=489702352871.dkr.ecr.us-west-2.amazonaws.com
IMAGE_NAME=scraper

build:
	docker-compose build web-scraper

tag:
	docker tag scraper:latest $(REGISTRY)/$(IMAGE_NAME):latest

push: tag
	docker push $(REGISTRY)/$(IMAGE_NAME):latest

deploy: build push
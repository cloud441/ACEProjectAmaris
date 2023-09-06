PROJECT_ID=aceproject-397607
CRONJOB_IMAGE_REPOSITORY=cronjob-reddit
WEBAPP_IMAGE_REPOSITORY=web-app

WEBAPP_IMAGE_VERSION=1
WEBAPP_IMAGE=web-app-image-v$(WEBAPP_IMAGE_VERSION)

CRONJOB_IMAGE_VERSION=1
CRONJOB_IMAGE=cronjob-reddit-image-v$(CRONJOB_IMAGE_VERSION)


build-image-cronjob:
	docker build -t $(CRONJOB_IMAGE):latest -f config/cronjob_reddit/Dockerfile .

push-image-cronjob:
	docker tag $(CRONJOB_IMAGE):latest europe-west1-docker.pkg.dev/$(PROJECT_ID)/$(CRONJOB_IMAGE_REPOSITORY)/$(CRONJOB_IMAGE):latest
	docker push europe-west1-docker.pkg.dev/$(PROJECT_ID)/$(CRONJOB_IMAGE_REPOSITORY)/$(CRONJOB_IMAGE):latest


build-image-app:
	docker build -t $(WEBAPP_IMAGE):latest -f config/web_app/Dockerfile .

push-image-app:
	docker tag $(WEBAPP_IMAGE):latest europe-west1-docker.pkg.dev/$(PROJECT_ID)/$(WEBAPP_IMAGE_REPOSITORY)/$(WEBAPP_IMAGE):latest
	docker push europe-west1-docker.pkg.dev/$(PROJECT_ID)/$(WEBAPP_IMAGE_REPOSITORY)/$(WEBAPP_IMAGE):latest
from .base import docker_client
from storage_manager import convertSizeUnit
import docker

class Images:
    def __init__(self):
        self.docker_client = docker_client()

    def getAll(self):
        docker_images = self.docker_client.images.list()
        docker_images_list = []
        for image in docker_images:
            image_id = image.short_id
            image_tags = image.tags
            image_size = convertSizeUnit(size=image.attrs['Size'], from_unit="B", mode="str", round_to=None)
            image_created_orig = image.attrs['Created']
            image_created_split = image_created_orig.split('.')[0]
            image_created = image_created_split.split('T')[0] + " " + image_created_split.split('T')[1]
            for  tag in image_tags:
                image_repo = tag.split(':')[0]
                image_tag = tag.split(':')[1]
                image_dict = {
                    "uuid": image_repo + '&split' + image_id + '&split' + image_tag,
                    "repo": image_repo,
                    "tag": image_tag,
                    "id": image_id,
                    "size": image_size,
                    "created": image_created,
                }
                docker_images_list.append(image_dict)
        return docker_images_list
    
    def remove(self, name):
        image = self.docker_client.images.get(name)
        image.remove()
    
    def pull(self, name, notify=True):
        # Create "progress" notification that the image is being pulled
        try:
            self.docker_client.images.get(name)
            print("Image already exists")
            # Mark the "progress" notification as error, with the message "Image already exists"
        except docker.errors.ImageNotFound:
            print("Image does not yet exist")
            # Pull the image
            self.docker_client.images.pull(name)
            # Mark the "progress" notification as complete
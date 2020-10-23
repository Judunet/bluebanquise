# ██████╗ ██╗     ██╗   ██╗███████╗██████╗  █████╗ ███╗   ██╗ ██████╗ ██╗   ██╗██╗███████╗███████╗
# ██╔══██╗██║     ██║   ██║██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔═══██╗██║   ██║██║██╔════╝██╔════╝
# ██████╔╝██║     ██║   ██║█████╗  ██████╔╝███████║██╔██╗ ██║██║   ██║██║   ██║██║███████╗█████╗
# ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║▄▄ ██║██║   ██║██║╚════██║██╔══╝
# ██████╔╝███████╗╚██████╔╝███████╗██████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝██║███████║███████╗
# ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚══════╝
#
# base_module:
#    This module contains the Image class that is the mother class
#    for all images classes. You need to be in compliance with this
#    class when creating new diskless images classes.
#
# 2020 - David Pieters <davidpieters22@gmail.com>
# https://github.com/bluebanquise/bluebanquise - MIT license


# Import base modules
import os
import shutil
from datetime import datetime
import yaml
import logging
from abc import ABC, abstractmethod

# Import diskless modules
from utils import *
from image_manager import ImageManager


class Image(ABC):

    """ Abstract class representing an image
    This class is the mother class for all types of images.

    You must redefine the following methods when inherit:

        * create_new_image()     -> Define your own image creation process
        * remove_files()         -> Specify what files to remove when image was properly created
        * clean()                -> Specify what files to remove when image was not properly created (All possible files)

    You can redefine the following methods when inherit:
       
        * generate_files()       -> Contains methods to execute to create image
        * create_image_folders() -> Create your image folders
        * generate_file_system() -> Generate your image file system

    Normaly you don't have to redefine other methods in sub classes but also you can for a specific need.
    Please check all Image class methods that can be redefined before creating a new method in subclass
    """

    # All type of image has a boot_file_template
    boot_file_template = ''

    # Each image has it's own base directory in IMAGES_DIRECTORY directory
    IMAGES_DIRECTORY = '/var/www/html/preboot_execution_environment/diskless/images/'


    def __init__(self, name, *args):
        """Class consructor.
        The constructor take in argument the name of the image, and the creation arguments (in *args).
        To get an already existing image you have previously created you must call this constructor whith only image 'name' to load it.
        To create a new image you must call this constructor with image 'name' and all other class constructor arguments.
        When you redefine Image class constructor you must define your constructor and create_new_image method as following:

            def __init__(self, name, arg1 = None, arg2 = None, argX = None...): <- You must strictly follow this syntax with your custom args (arg1, arg2, argX ...) 
                super().__init__(name, arg1, arg2, argX...)                     <-
                                                                                <-
            def create_new_image(self, arg1, arg32, argX...):                   <-
                ...(your code)                                                  <- From here you can custom

        For an exemple look at DemoClass class in demo_module

        :param name: The name of the image
        :type name: str
        :param *args: The list of arguments for image creation
        :type *args: list of arguments
        """

        # Check name format
        if len(name.split()) > 1 or not isinstance(name, str):
            raise ValueError('Invalid name format.')

        # Set up image name
        self.name = name

        # Set up image directory, it is a mandatory directory for all images
        self.IMAGE_DIRECTORY = Image.IMAGES_DIRECTORY + self.name
        
        # If image already exist, and not all other arguments excepts name are None: 
        # Bad usage of constructor
        if os.path.isdir(self.IMAGE_DIRECTORY) and not all(arg is None for arg in args):
            raise ValueError('Bad constructor image: All arguments must be None except name when image already exist')

        # If the image already exist, and all other arguments excepts name are None:
        # Load existing image
        elif os.path.isdir(self.IMAGE_DIRECTORY):
            logging.debug('Loading existing image')
            # Use image class method to get image 
            self.get_existing_image()

        # If image don't already exist, create it
        else:
            # Create the base mandatory directory the image
            os.mkdir(self.IMAGE_DIRECTORY)
            logging.info('Starting image creation...')

            # Register image in ongoing installations file
            ImageManager.register_installation(self.name, self.__class__.__name__)

            # Create the image object with all constructor arguments except the name because it is already an image attribute
            self.create_new_image(*args)

            # Register all image attributs at the end of its creation for saving it
            self.register_image()

            # After image creation, unregister it from ongoing installations file
            ImageManager.unregister_installation(self.name)
            logging.info('Image creation complete !')

    @abstractmethod
    def create_new_image(self):
        """Create a new image. This method must be redefined in all subclasses."""
        logging.info('Creating new image' + self.name)

    @abstractmethod
    def remove_files(self):
        """Remove all files of a created image when the image was properly created.
        This method must be redefined in all subclasses."""
        logging.info('Removing image ' + self.name + ' files...')

        # Remove image base directory
        if os.path.isdir(self.IMAGE_DIRECTORY):
            shutil.rmtree(self.IMAGE_DIRECTORY)

    @staticmethod
    @abstractmethod
    def get_boot_file_template():
        """Get the class boot file template.
        This method must be redefined in all Image subclasses."""
        return ''

    @staticmethod
    @abstractmethod
    def clean(image_name):
        """ Clean all files of an image without the need of an image object.
        It is usefull to clean all files when an image has crashed during it's creation.
        This method must be redefined in all Image subclasses.
        The redefinition must clean all possible remaining image files.

        :param image_name: The name of the image to clean
        :type image_name: str
        """
        logging.info('Cleaning image ' + image_name + 'files...')

    def generate_files(self):
        """Generate image files."""
        logging.info('Starting generating image files...')
        self.create_image_folders()
        self.generate_ipxe_boot_file()
        self.generate_file_system()

    def create_image_folders(self):
        """Create image folders."""
        logging.info('Image folders creation')

    def generate_file_system(self):
        """Generate image file system."""
        logging.info('Installing new system image... May take some time.')
    
    def register_image(self):
        """Register the image data into it's 'image_data' file.
        This file is a save of the image.
        To load an existing image this file is mandatory because it contains all image attributs."""
        logging.info('Registering the image')

        # Add creation date to image attributes, it is the date of image registering (current date)
        self.image_class = self.__class__.__name__
        self.creation_date = datetime.today().strftime('%Y-%m-%d')

        file_content = 'image_data:\n    '

        # For all image attributes
        for attribute, value in self.__dict__.items():
            # Register attribute
            file_content = file_content + '\n    ' + attribute + ': ' + str(value)
          
        # Creating or edit the image_data file that contains image attributes in yaml
        with open(self.IMAGE_DIRECTORY + '/image_data.yml', "w") as ff:
            ff.write(file_content)

    def get_image_data(self):
        """Getting image data that has been writen inside the image image_data.yml during register_image() call."""
        # Reading image_data file
        with open(self.IMAGE_DIRECTORY + '/image_data.yml', 'r') as f:
            # Getting all data
            data = yaml.safe_load(f)
            # Getting image_data
            image_data = data['image_data']

        # Return the array of data
        return image_data

    def get_existing_image(self):
        """Load an existing image. The loading consist of getting all image attributes from it's image_data.yml file."""
        logging.debug("Getting existing image")
        
        # Get image data
        image_data = self.get_image_data()

        # Set all image attributes with image data
        for attribute_key, attribute_value in image_data.items():
            setattr(self, attribute_key, attribute_value)

    # Change image kernel
    def set_kernel(self, kernel):
        """Change the kernel of the image.

        :param kernel: The kernel to set to the image
        :type kernel: str
        """
        logging.info('Set up image kernel')
        # Change image kernel attibute
        self.kernel = kernel
        # Regenerate ipxe boot file
        self.generate_ipxe_boot_file(self.get_ipxe_boot_file())
        #Register image with new kernel
        self.register_image()

    def generate_ipxe_boot_file(self):
        """Generate an ipxe boot file for the image."""
        logging.info('Creating IPXE boot file for the image')
        # Format image ipxe boot file template with image attributes
        file_content = self.__class__.get_boot_file_template().format(image_name=self.name, 
                                                                image_initramfs=self.image,
                                                                image_kernel=self.kernel)

        # Create ipxe boot file
        with open(self.IMAGE_DIRECTORY + '/boot.ipxe', "w") as ff:
            ff.write(file_content)

    @classmethod
    def get_images(cls):
        """Get all images that are of this class type."""
        # Get all images
        images = ImageManager.get_created_images()

        # Instantiate None class_image array
        class_images = None
        # If there is images
        if images:
            # Get all class images
            class_images = [image for image in images if image.image_class == cls.__name__]

        # Return all class images
        return class_images


    ######################
    ## CLI reserved part##
    ######################

    def cli_display_info(self):
        """Display informations about an image"""
        # Get image_data, it is a dictionary with all the image attributes
        image_data = self.get_image_data()

        # Print image name
        print(' • Image name: ' + image_data['name'])

        # Remove name element from image_data list
        del image_data['name']

        # For each tuple of list except the last
        for i in range(0, len(image_data.items()) - 1):
            print('     ├── ' + str(list(image_data.keys())[i]) + ': ' + str(list(image_data.values())[i]))

        # For the last tuple element of the list
        print('     └── ' + str(list(image_data.keys())[-1]) + ': ' + str(list(image_data.values())[-1]))

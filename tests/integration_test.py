# from __future__ import print_function

# import random

# import os
# import sys
# from os import path

# from wanna import Transfer

# import logging

# logging.basicConfig(format="%(levelname)-8s %(message)s")

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setLevel(logging.DEBUG)
# logger.addHandler(console_handler)

# application_profile_space = Transfer(
#     vendor="aws", bucket="mr17-external-prd-15", profile="mr-app-user-prd")

# user_profile_space = Transfer(
#     vendor="aws", bucket="mr17-external-prd-15", profile="mr17-external-prd-15")

# module_dir = os.path.dirname(os.path.realpath(__file__))

# random_file_name = "%032x" % random.getrandbits(128)
# file_path = os.path.join(module_dir, random_file_name)


# try:
#     shared_secret = "cf243a7c213899020c18b76a2dff7226a570723100e49d9d067cd4759e0a02bb"

#     logger.debug('creating file %s' % file_path)
#     file_stub = open(file_path, "w+")
#     file_stub.write(random_file_name)
#     file_stub.close()

#     # Upload file and remove locally
#     logger.debug("uploading %s" % file_path)

#     application_profile_space.upload_files(
#         file_path, encryption_key=shared_secret)

#     # Download file and assert
#     logger.debug("downloading %s" % random_file_name)

#     user_profile_space.download_file(
#         random_file_name, dst=file_path + ".download", encryption_key=shared_secret)

#     assert os.path.isfile(file_path) == True

#     with open("{}.download".format(file_path)) as f:
#         assert f.readline() == random_file_name

#     # Clean files
#     user_profile_space.delete_file(random_file_name)
#     logger.debug("removing %s" % file_path)
#     os.remove(file_path)
#     os.remove("{}.download".format(file_path))

#     logger.info('test succeeded')
# except OSError as e:
#     print("ERROR %s" % e.message)
#     raise
# except IOError as e:
#     print("ERROR %s" % e.message)
#     raise
# except:
#     print("Unexpected error:", sys.exc_info()[0])
#     raise

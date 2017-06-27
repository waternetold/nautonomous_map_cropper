#!/usr/bin/env python

from PIL import Image
import rospy

from geometry_msgs.msg import Pose2D
from nautonomous_map_msgs.srv import Crop, CropResponse

import image_cropper	

# Create the service so other nodes can request to crop the map.
def crop_map_points_service(request):
	image_name, config_name = image_cropper.crop_map_points(request.route, request.name)

  	return CropResponse(image_name, config_name)
	
def main():
	global initial_pose_pub
	rospy.init_node('passive_map_cropper_node')

	print "Passive map cropper"
	image_cropper.load_full_image()

	s = rospy.Service('/map/cropper/crop', Crop, crop_map_points_service)

	rospy.spin()

if __name__ == '__main__':
	main()


import math
import rospy
import rospkg

from PIL import Image
import yaml

from geometry_msgs.msg import Pose2D

rospack = rospkg.RosPack()

nautonomous_configuration_path = rospack.get_path('nautonomous_configuration')

original_image = None
original_name = "amsterdam"

negate_image = False


# Load the entire image of amsterdam so we can use it to crop it.
def load_original_image(image_name):
	global original_image, original_name
	original_name = image_name
	full_image_string = nautonomous_configuration_path + "/config/map/"+ str(original_name) + ".png"
	original_image = Image.open(full_image_string)

# Crop the map using a list of points
def crop_map_points(points,	name_map):
    global original_image, negate_image
	
    negate_image = rospy.get_param('~negate_image_param', False)
    print "NEGATE " + str(negate_image)
    map_data = open_original_config_file()
    # extract the position of the cropped map
    resolution, left_position, right_position, bottom_position, top_position = extract_cropped_image_positions(map_data, points)
    # save the cropper image based on the positions
    save_cropped_image(original_image, name_map, resolution, left_position, right_position, bottom_position, top_position)
    # save the config file based on the positions
    config_file_name =  save_config_file(name_map, map_data, left_position, right_position, bottom_position, top_position)

    return config_file_name

# Open the config file from the original image
def open_original_config_file():
	global original_name
	with open(nautonomous_configuration_path + "/config/map/" + str(original_name) + ".yaml") as f:
		map_data = yaml.safe_load(f)
	return map_data

# Extract the cropped image positions based on the positions of the nodes in the map.
def extract_cropped_image_positions(map_data, nodes):
    # get map parameters
	resolution = map_data["resolution"]
	map_left = map_data["map_left"]
	map_top = map_data["map_top"]
	map_bottom = map_data["map_bottom"]

    # Get the transformed nodes in the full image frame
	nodes_x = []
	nodes_y = []
	for node in nodes:
		nodes_x.append(node.x - map_left)
		nodes_y.append(map_top - node.y)
	
    #TODO add the theta parameter to more efficiently crop the image.
	# edge_width = abs(first_node_x - second_node_x)
	# edge_height = abs(first_node_y - second_node_y)
	# theta = math.atan2( edge_height, edge_width)
	# print "Theta: " + str(theta)

    #TODO dynamic margin
	# margin for top, left, bottom and right
	margin = 50 # magic 50 meters boundary

	# find rectangle that fits the path
	left_position = min(nodes_x) - margin
	right_position = max(nodes_x) + margin
	bottom_position = max(nodes_y) + margin
	top_position = min(nodes_y) - margin

	return resolution, left_position, right_position, bottom_position, top_position

# Save the cropped image based on the cropped positions
def save_cropped_image(original_image, file_name, resolution, left_position, right_position, bottom_position, top_position):
    # create cropped image
	cropped_example = original_image.crop(
		(
			int(left_position / resolution),  
			int(top_position / resolution), 
			int(right_position / resolution), 
			int(bottom_position / resolution)
		)
	)
	cropped_example.save(nautonomous_configuration_path + "/config/map/" + str(original_name) + "_cropped_" + str(file_name) + ".png")

# Save config file based on the cropped positions
def save_config_file(file_name, map_data, left_position, right_position, bottom_position, top_position):
	# create cropped config file
	map_left = map_data["map_left"]
	map_right = map_data["map_right"]
	map_bottom = map_data["map_bottom"]
	map_top = map_data["map_top"]

	map_data["map_left"] = left_position
	map_data["map_right"] = right_position
	map_data["map_bottom"] = bottom_position
	map_data["map_top"] = top_position
	map_data["image"] = nautonomous_configuration_path + "/config/map/" + str(original_name) + "_cropped_" + str(file_name) + ".png"
	map_data["origin"] = [left_position+map_left, (map_top - map_bottom) - bottom_position + map_bottom, 0.0]
	negate_image_value = 0
	if negate_image:
		print "set NEGATE 1"
		negate_image_value = 1

	map_data["negate"] = negate_image_value

    # Save the image and config name
	config_name = nautonomous_configuration_path + "/config/map/" + str(original_name) + "_cropped_" + str(file_name) + ".yaml"
 
    # Open the config file and dump the data
	with open(config_name, "w") as f:
		yaml.dump(map_data, f)

    # return the image and config file name
	return config_name

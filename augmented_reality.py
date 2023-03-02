import cv2
import numpy as np
import matplotlib.pyplot as plt
import mime
import mimetypes
from helper_methods import *

# Printing and Placement of ArUco Markes to Define a ROI
mimetypes.init()

# Specify the name of inputed videos and the id of the used markers
input_vids = ['Animated Cover.mp4', 'Macbook Promo Vid.mp4']
marker_ids = [23, 25, 33, 30]  # Upper left, upper right, lower right, lower left

# Scale factors used to increase size of source media to cover ArUco Marker borders.
scaling_fac_x = .008 
scaling_fac_y = .012

class MediaSpec:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        
media_spec = MediaSpec(input_vids[0], input_vids[1])

# Create a video capture object from the source video
src_input = media_spec.src
cap_src = cv2.VideoCapture(src_input)
fps = cap_src.get(cv2.CAP_PROP_FPS)

# Create a video capture object from the destination video
dst_input = media_spec.dst
cap_dst = cv2.VideoCapture(dst_input)
fps = cap_dst.get(cv2.CAP_PROP_FPS)

output_file = 'Macbook with Animated Cover.mp4'
    
# Determine the output video size based on the destination video frame size.
width = round(2 * cap_dst.get(cv2.CAP_PROP_FRAME_WIDTH))
height = round(cap_dst.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create the video writer object.
video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# Initial values for frame-looping 
src_has_frame = True
dst_has_frame = True
frame_count = 0
max_frames = 100
color = (255, 255, 255)
ref_points = ([0,0], [0,0], [0,0], [0,0])

# Load the dictionary that was used to generate the markers.
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Process Source and Destination Frames
print('Processing frames ...')
while src_has_frame & dst_has_frame:

    # Get frame from the destination video.
    dst_has_frame, frame_dst = cap_dst.read()
    if not dst_has_frame:
        break

    # The source is a video, so retrieve the source frame.
    src_has_frame, frame_src = cap_src.read()
    if not src_has_frame:
        break
 
    # Resize the image to have a height of 200 pixels, auto width
    HEIGHT = 2000
    r = HEIGHT / frame_dst.shape[0]
    dim = (int(frame_dst.shape[1] * r), HEIGHT)
    frame_resize = cv2.resize(frame_dst, dim, interpolation = cv2.INTER_AREA)

    # Detect the markers in the image.
    corners, ids, rejected = cv2.aruco.detectMarkers(frame_resize, dictionary)
    corners = list(map(lambda corner: corner / r, corners))
    
    # Extract reference point coordinates from marker corners.
    ref_pt1, ref_pt2, ref_pt3, ref_pt4 = extract_pts(marker_ids, ids, corners, ref_points)
    ref_points = (ref_pt1, ref_pt2, ref_pt3, ref_pt4)

    # Scale destination points.
    pts_dst = scale_dst_points(ref_pt1, ref_pt2, ref_pt3, ref_pt4, 
                                   scaling_fac_x = scaling_fac_x, 
                                   scaling_fac_y = scaling_fac_y)

    # The source points are the four corners of the image source frame.
    pts_src = [[0,0], [frame_src.shape[1], 0], [frame_src.shape[1], frame_src.shape[0]], [0, frame_src.shape[0]]]

    # Convert list of points to arrays.
    pts_src_m = np.asarray(pts_src)
    pts_dst_m = np.asarray(pts_dst)

    # Calculate the homography.
    h, mask = cv2.findHomography(pts_src_m, pts_dst_m, cv2.RANSAC)

    # Warp source image onto the destination image.
    warped_image = cv2.warpPerspective(frame_src, h, (frame_dst.shape[1], frame_dst.shape[0]))

    # Prepare a mask representing the region to copy from the warped image into the destination frame.
    mask = np.zeros([frame_dst.shape[0], frame_dst.shape[1]], dtype=np.uint8);
     
    # Fill ROI in destination frame with white to create mask.
    cv2.fillConvexPoly(mask, np.int32([pts_dst_m]), (255, 255, 255), cv2.LINE_AA);

    # Copy the mask into 3 channels.
    warped_image = warped_image.astype(float)
    mask3 = np.zeros_like(warped_image)
    for i in range(0, 3):
        mask3[:, :, i] = mask / 255
    
    # Create black region in destination frame ROI.
    frame_masked = cv2.multiply(frame_dst.astype(float), 1 - mask3)
    
    # Create final result by adding warped image with the masked destination frame.
    frame_out = cv2.add(warped_image, frame_masked)

    # Showing the original frame and the new output frame side by side.
    concatenated_output = cv2.hconcat([frame_dst.astype(float), frame_out])

    # Draw a white vertical line that divides the two image frames.
    frame_w = concatenated_output.shape[1]
    frame_h = concatenated_output.shape[0]
    concatenated_output = cv2.line(concatenated_output, 
                                   (int(frame_w / 2), 0), 
                                   (int(frame_w / 2), frame_h), 
                                   color, thickness = 8)

    # Create output file.
    video_writer.write(concatenated_output.astype(np.uint8))
        
cv2.destroyAllWindows()
if 'video_writer' in locals():
    video_writer.release()
    print('Processing complete, video writer released ...')
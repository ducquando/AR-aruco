import numpy as np

# Extract reference point coordinates from marker corners
def extract_pts(marker_ids, ids, corners, ref_points):
    # Previous location
    ref_pt1, ref_pt2, ref_pt3, ref_pt4 = ref_points[:4]
    
    # Upper left corner of ROI.
    index = np.squeeze(np.where(ids == marker_ids[0]))
    if index.size > 0:
        ref_pt1 = np.squeeze(corners[index[0]])[0]

    # Upper right corner of ROI.
    index = np.squeeze(np.where(ids == marker_ids[1]))
    if index.size > 0:
        ref_pt2 = np.squeeze(corners[index[0]])[1]
        
    # Lower right corner of ROI.
    index = np.squeeze(np.where(ids == marker_ids[2]))
    if index.size > 0:
        ref_pt3 = np.squeeze(corners[index[0]])[2]

    # Lower left corner of ROI.
    index = np.squeeze(np.where(ids == marker_ids[3]))
    if index.size > 0:
        ref_pt4 = np.squeeze(corners[index[0]])[3]

    return ref_pt1, ref_pt2, ref_pt3, ref_pt4

# Scale destination points
def scale_dst_points(ref_pt1, ref_pt2, ref_pt3, ref_pt4, scaling_fac_x = 0.01, scaling_fac_y = 0.01):
    # Compute horizontal and vertical distance between markers.
    x_distance = np.linalg.norm(ref_pt1 - ref_pt2)
    y_distance = np.linalg.norm(ref_pt1 - ref_pt3)

    delta_x = round(scaling_fac_x * x_distance)
    delta_y = round(scaling_fac_y * y_distance)

    # Apply the scaling factors to the ArUco Marker reference points to make
    # the final adjustment for the destination points.
    pts_dst = [[ref_pt1[0] - delta_x, ref_pt1[1] - delta_y]]
    pts_dst = pts_dst + [[ref_pt2[0] + delta_x, ref_pt2[1] - delta_y]]
    pts_dst = pts_dst + [[ref_pt3[0] + delta_x, ref_pt3[1] + delta_y]]
    pts_dst = pts_dst + [[ref_pt4[0] - delta_x, ref_pt4[1] + delta_y]]

    return pts_dst
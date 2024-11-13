### Pre-Process CDL Data
### Adam Gallaher, Ph.D.
### Cornell University
### 7-2-24


import arcpy
import os

## define preprocess function

def process_raster(input_folder, output_folder, mask_path, ag_values, reproj_crs_epsg, snap_raster_path=None):
    arcpy.env.workspace = input_folder
    arcpy.env.overwriteOutput = True

    # Set the snap raster if provided
    if snap_raster_path:
        arcpy.env.snapRaster = snap_raster_path


    ## list all raster datasets in input folder
    rasters = arcpy.ListRasters()

    reproj_crs = arcpy.Describe(reproj_crs_epsg).SpatialReference

    for raster in rasters:
        try:

            ## Reclassify raster based on remap values
            out_reclassified_raster = os.path.join(output_folder, f"reclass_{raster}")
            remap = arcpy.sa.RemapValue([[val, 1] if val in ag_values else [val, 0] for val in range(256)])
            reclassified_raster = arcpy.sa.Reclassify(raster, "Value", remap, "NODATA")

            ## save reclassified raster
            reclassified_raster.save(out_reclassified_raster)

            ## Reproject raster to desired coordinate system
            out_reprojected_raster = os.path.join(output_folder, f"proj_{raster}")
            arcpy.management.ProjectRaster(out_reclassified_raster, out_reprojected_raster, reproj_crs)

            ## Extract by mask
            out_extracted_raster = os.path.join(output_folder, f"mask_{raster}")
            arcpy.sa.ExtractByMask(out_reprojected_raster, mask_path).save(out_extracted_raster)

            ## clean up intermediate recalssified raster
            arcpy.Delete_management(out_reclassified_raster)
            ## clean up intermediate reprojected raster
            arcpy.Delete_management(out_reprojected_raster)

            print(f"Processed {raster}")
        except Exception as e:
            print(f"Failed to process {raster}: {str(e)}")

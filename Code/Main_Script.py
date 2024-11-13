### main pre-processing script for ethanol paper
## Adam Gallaher, Ph.D.
## Cornell University
## 7-2-24

import os 
import arcpy
from arcpy.sa import * 
from CDL_Preprocess import process_raster

if __name__ == "__main__":

    input_folder = r"folder containing CDL raster data"
    output_folder = r"output folder for results"
    mask_path = r"path for file representing the study area (e.g., shapefile of CONUS)"
  
    ag_values = [1, 225, 226, 228, 237, 241] ## CDL values for agriculture land use, can be changed for different crops
  
    reproj_crs_epsg = r"raster file used to reproject all data in input folder to prefered coordinate reference system"
    snap_raster_path = r"raster file used to align all cells in input data folder"


    #process_raster(input_folder, output_folder, mask_path, ag_values, reproj_crs_epsg, snap_raster_path)
    
    # Add new field and calculate values
    arcpy.CheckOutExtension("Spatial")
    
    arcpy.env.workspace = output_folder
    arcpy.env.overwriteOutput = True
    rasters = arcpy.ListRasters()
    print(rasters)

    combine_rasters = []

    for raster in rasters:
        try:
            # Add new field specifying corn (1) or not corn (0)
            arcpy.management.AddField(raster, "Corn_Flag", "SHORT")
            arcpy.management.CalculateField(raster, "Corn_Flag", "1 if !VALUE! == 1 else 0", "PYTHON3")
            print("Finished add field for: {}".format(raster))
            

            ## apply minimum mapping unit
            RegionGroup_Raster = os.path.join(output_folder, f"Gr_{raster}")
            outRegionGroup = RegionGroup(raster, "EIGHT", "WITHIN", "ADD_LINK", "")
            outRegionGroup.save(RegionGroup_Raster)
            print("Finished region group for: {}".format(raster))

            SetNull_Raster = os.path.join(output_folder, f"Fin_{raster}")
            combine_rasters.append(SetNull_Raster)
            outSetNull = SetNull(outRegionGroup, 1, "Count < 24 OR LINK = 0")
            outSetNull.save(SetNull_Raster)
            print("Finished set null for: {}".format(raster))

            arcpy.Delete_management(RegionGroup_Raster)
            print("Deleting rasters...")
            

        except Exception as e:
            print(f"Failed to add field and calculate values for {raster}: {str(e)}")

    output_mosaic = os.path.join(output_folder, f"Ag_mosaic_L48.tif")
    reproj_crs = arcpy.Describe(reproj_crs_epsg).SpatialReference

    print("Working on mosaic raster")
    arcpy.MosaicToNewRaster_management(combine_rasters,
                                       output_folder, # needs to be folder name
                                       output_mosaic,# needs to be file name (currently full path name). 
                                       reproj_crs,
                                       "8_BIT_UNSIGNED", "30", "1", "SUM", "FIRST")
                                       
    print("Processing complete.")

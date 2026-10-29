import subprocess
import json
import pandas as pd

INPUT = "copenaghen.csv"
OUTPUT = "dataset_with_metadata.csv"

df = pd.read_csv(INPUT)

# Map of column names in CSV -> possible keys in exiftool JSON
TAG_MAP = {
    # dimensions / format
    "ImageWidth": ["ImageWidth", "ExifImageWidth", "PixelXDimension"],
    "ImageHeight": ["ImageHeight", "ExifImageHeight", "PixelYDimension"],
    "Megapixels": ["Megapixels"],
    "BitsPerSample": ["BitsPerSample"],
    "ColorComponents": ["ColorComponents"],
    "YCbCrSubSampling": ["YCbCrSubSampling"],
    "EncodingProcess": ["EncodingProcess"],
    "ImageSize": ["ImageSize"],
    "FileType": ["FileType"],
    "FileTypeExtension": ["FileTypeExtension"],
    "MIMEType": ["MIMEType"],
    "FileSize": ["FileSize"],

    # ICC profile / colors
    "ProfileCMMType": ["ProfileCMMType"],
    "ProfileVersion": ["ProfileVersion"],
    "ProfileClass": ["ProfileClass"],
    "ColorSpaceData": ["ColorSpaceData"],
    "ProfileConnectionSpace": ["ProfileConnectionSpace"],
    "ProfileDateTime": ["ProfileDateTime"],
    "ProfileFileSignature": ["ProfileFileSignature"],
    "PrimaryPlatform": ["PrimaryPlatform"],
    "CMMFlags": ["CMMFlags"],
    "DeviceManufacturer": ["DeviceManufacturer"],
    "DeviceModel": ["DeviceModel"],
    "DeviceAttributes": ["DeviceAttributes"],
    "RenderingIntent": ["RenderingIntent"],
    "ConnectionSpaceIlluminant": ["ConnectionSpaceIlluminant"],
    "ProfileCreator": ["ProfileCreator"],
    "ProfileID": ["ProfileID"],
    "ProfileDescription": ["ProfileDescription"],
    "ProfileCopyright": ["ProfileCopyright"],
    "MediaWhitePoint": ["MediaWhitePoint"],
    "RedMatrixColumn": ["RedMatrixColumn"],
    "GreenMatrixColumn": ["GreenMatrixColumn"],
    "BlueMatrixColumn": ["BlueMatrixColumn"],
    "RedTRC": ["RedTRC"],
    "GreenTRC": ["GreenTRC"],
    "BlueTRC": ["BlueTRC"],

    # IPTC residual
    "CurrentIPTCDigest": ["CurrentIPTCDigest"],
    "SpecialInstructions": ["SpecialInstructions"],

    # Image quality/resolution
    "XResolution": ["XResolution"],
    "YResolution": ["YResolution"],

    # File system
    "FileModifyDate": ["FileModifyDate"],
    "FileAccessDate": ["FileAccessDate"],

    # camera identity
    "Make": ["Make"],
    "Model": ["Model"],
    "LensModel": ["LensModel"],
    "FocalLength": ["FocalLength"],
    "ISO": ["ISO"],
    "ExposureTime": ["ExposureTime"],
    "Aperture": ["ApertureValue"],
    "WhiteBalance": ["WhiteBalance"],

    # editing / processing
    "Software": ["Software", "CreatorTool", "HistorySoftware"],
    "ModifyDate": ["ModifyDate"],

    # forensics
    "Orientation": ["Orientation"],
    "JPEGQuality": ["JPEGQualityEstimate"],
    "JFIFVersion": ["JFIFVersion"],

    # GPS
    "GPSLatitude": ["GPSLatitude"],
    "GPSLongitude": ["GPSLongitude"],
    "GPSAltitude": ["GPSAltitude"],

    # Duplication check
    "MD5": ["MD5", "DocumentID", "InstanceID"],
}


metadata_columns = {col: [] for col in TAG_MAP.keys()}

for path in df["filepath"]:
    try:
        result = subprocess.run(
            ["exiftool", "-j", path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0 or not result.stdout.strip():
            meta = {}
        else:
            meta_list = json.loads(result.stdout)
            meta = meta_list[0] if meta_list else {}

        for col_name, possible_keys in TAG_MAP.items():
            value = None
            for key in possible_keys:
                if key in meta:
                    value = meta[key]
                    break
            metadata_columns[col_name].append(value)

    except Exception:
        for col_name in TAG_MAP.keys():
            metadata_columns[col_name].append(None)


for col_name, values in metadata_columns.items():
    df[col_name] = values

df.to_csv(OUTPUT, index=False)
print("saved:", OUTPUT)




metadata_df = pd.read_csv("dataset_with_metadata.csv")

# Percentage of non-null values per column
non_null_ratio = 1 - metadata_df.isna().mean()
print(non_null_ratio.sort_values())

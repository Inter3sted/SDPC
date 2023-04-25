# The first few lines are import statements that bring in the necessary libraries for working with PNG files, random number generation, regular expressions, and operating system functionality.
import png
import random
import re
import os

# Extract PNG chunks from PNGs
from PIL import Image
# takes a filepath as an argument, reads in the PNG file at that path, and extracts the metadata associated with the image. 
# Specifically, it looks for chunks of data in the PNG file that are labeled as "tEXt" and have the keyword "parameters" in them. 
# If such a chunk is found, the function returns a dictionary containing the metadata.
def get_png_metadata(filepath):
    try:
        with open(filepath, 'rb') as f:
            pngdata = png.Reader(file=f)
            metadata = {}
            for chunk_type, chunk_data in pngdata.chunks():
                if chunk_type == b'tEXt':
                    if b'parameters' in chunk_data:
                        metadata[chunk_type] = chunk_data
            return metadata
    except (png.FormatError, PermissionError) as e:
        print(f"Skipping file {filepath} due to {type(e).__name__}.")
        return None

# Filter metadata and only get the tags
# takes the metadata dictionary returned by get_png_metadata and extracts the actual tags from it. 
# It does this by decoding the metadata's bytes into a UTF-8 string, finding the position in the string where the "parameters" keyword is, and then taking the characters after that keyword and before the next newline character as the tag string.
def extract_metadata_string(metadata):
    if b'tEXt' in metadata:
        metadata_str = metadata[b'tEXt'].decode("utf-8")
        start = metadata_str.index("parameters") + len("parameters")
        end = metadata_str.index("\n", start)
        return metadata_str[start:end]
    else:
        return ""

# The script starts by specifying the folder path where the PNG files to be processed are located.
folder_path = r"your directory path"

# It then creates a list of filenames in that folder using the os.listdir function.
png_files = os.listdir(folder_path)

# The script then loops through each file in the folder and calls the get_png_metadata and extract_metadata_string functions on it to get the tags associated with each image. These tags are appended to a list called png_metadata.
png_metadata = []
for png_file in png_files:
    filepath = os.path.join(folder_path, png_file)
    metadata = get_png_metadata(filepath)
    if metadata is not None:
        png_metadata.append(extract_metadata_string(metadata).split(','))

# The tag_extraction_ratio variable is set to 1, which means that the script will extract all tags from each image. This can be changed to a value between 0 and 1 to extract a fraction of the tags.
tag_extraction_ratio = 1 # change variable to control number of tags extracted
# The extracted_tags list is created and then populated by randomly selecting tags from each image's list of tags. The number of tags selected from each image is determined by multiplying the length of that image's tag list by tag_extraction_ratio.
extracted_tags = []
for metadata_list in png_metadata:
    num_tags_per_image = int(len(metadata_list) * tag_extraction_ratio)
    extracted_tags.extend(random.sample(metadata_list, num_tags_per_image))

# The script then removes any duplicate tags from the extracted_tags list by converting it to a set and then back to a list.
extracted_tags = list(set(extracted_tags))

# Finally, the extracted_tags list is joined into a single string with the tags separated by commas, and that string is printed to the console.
output = ','.join(extracted_tags)
print(output)

import pydicom
import shutil
import glob
import os

def is_compressed(dicom_file):
    #ds = pydicom.dcmread(dicom_file, stop_before_pixels=True)
    #compressed_uids = pydicom.uid.JPEG2000TransferSyntaxes
    #return ds.file_meta.TransferSyntaxUID in compressed_uids
    return True

def decompress_dicom(input_file, output_file):
    # Read the DICOM file
    ds = pydicom.dcmread(input_file)

    # Check if the file is already uncompressed
    if not is_compressed(input_file):
        print(f"{input_file} is not compressed. Copying to output...")
        shutil.copy(input_file, output_file)
        return

    # Decompress the pixel data (using ds.pixel_array automatically invokes gdcm if needed)
    print(f"Decompressing {input_file}...")
    pixel_array = ds.pixel_array

    # Update the DICOM metadata to indicate uncompressed data
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    ds.PixelData = pixel_array.tobytes()

    # Save the decompressed DICOM file
    ds.save_as(output_file)
    print(f"Decompressed file saved as: {output_file}")

def find_dcm_files(folder_path):
    # Search for all files with .dcm extension in the specified folder
    dcm_files = glob.glob(os.path.join(folder_path, "*.dcm"))
    return dcm_files

def find_all_files(folder_path):
    # Search for all files in the specified folder
    dcm_files = glob.glob(os.path.join(folder_path, "*"))
    return dcm_files

# List of common file extensions
common_extensions = {
    '.txt', '.csv', '.jpg', '.png', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.mp3', '.mp4', '.avi', '.mov', '.zip', '.tar', '.gz',
    '.html', '.htm', '.xml', '.json', '.py', '.java', '.c', '.cpp', '.js',
    '.css', '.php', '.rb', '.go', '.sh', '.bat', '.md', '.ini', '.log'
}

def is_common_file(filename):
    # Extract the file extension and check if it's in the known set
    _, extension = os.path.splitext(filename)
    return extension.lower() in common_extensions

if __name__ == '__main__':
    # Example usage
    #folder_path = "W:\RadOnc\Physics\Temp\S0000001"
    folder_path = "U:/temp/CT_OT_PT_SD_8533502_20241210124203_1"
    out_dir = os.path.join(folder_path, 'decompressed')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    files = find_dcm_files(folder_path)

    if len(files) == 0:
        files = find_all_files(folder_path)

    for file in files:

        if is_common_file(file):
            print(f'Not dicom file: {file}')
            continue

        filename = os.path.basename(file)
        print(f"Processing {filename}...")
        out_file = os.path.join(out_dir, filename)

        try:
            decompress_dicom(file, out_file)
        except Exception as e:
            print(f"Error: decompression failed for {file}, {e}")

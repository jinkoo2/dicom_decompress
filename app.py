import pydicom
import shutil
import glob
import os

def is_compressed(dicom_file):
    ds = pydicom.dcmread(dicom_file, stop_before_pixels=True)
    compressed_uids = [
        pydicom.uid.JPEGBaseline,
        pydicom.uid.JPEGExtended,
        pydicom.uid.JPEGLossless,
        pydicom.uid.JPEGLosslessNonHierarchical,
        pydicom.uid.JPEGLSLossless,
        pydicom.uid.JPEGLSLossy,
        pydicom.uid.JPEG2000Lossless,
        pydicom.uid.JPEG2000,
        pydicom.uid.RLELossless
    ]
    return ds.file_meta.TransferSyntaxUID in compressed_uids

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

if __name__ == '__main__':
    # Example usage
    folder_path = "U:\\temp\\CT_SD_8240456_20241031135416_1"
    out_dir = os.path.join(folder_path, 'decompressed')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    dcm_files = find_dcm_files(folder_path)
    
    for dcm_file in dcm_files:
        filename = os.path.basename(dcm_file)
        print(f"Processing {filename}...")
        out_file = os.path.join(out_dir, filename)

        try:
            decompress_dicom(dcm_file, out_file)
        except Exception as e:
            print(f"Error: decompression failed for {dcm_file}, {e}")

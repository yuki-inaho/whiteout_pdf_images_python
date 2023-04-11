import io
import sys
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter


def process_page(page):
    output = io.BytesIO()
    xObject = page["/Resources"]["/XObject"].get_object()

    for obj in xObject:
        if xObject[obj]["/Subtype"] == "/Image":
            size = (xObject[obj]["/Width"], xObject[obj]["/Height"])
            data = xObject[obj].get_data()
            image = Image.frombytes("RGB", size, data, "raw", "BGR", 0, 1)

            # White out the image
            white_image = Image.new("RGB", size, "white")
            image = white_image

            # Save the white image as JPEG in memory
            image.save(output, "JPEG")

            # Replace the original image data with the white image data
            xObject[obj]._data = output.getvalue()
    return page


def whiteout_images(input_pdf, output_pdf):
    # Read the input PDF
    reader = PdfReader(input_pdf)

    # Create a PDF writer for the output PDF
    writer = PdfWriter()

    # Process each page and add it to the output PDF
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        if "/XObject" not in page["/Resources"].keys():
            continue
        processed_page = process_page(page)
        writer.add_page(processed_page)

    # Write the output PDF
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)


if __name__ == "__main__":
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    whiteout_images(input_pdf, output_pdf)

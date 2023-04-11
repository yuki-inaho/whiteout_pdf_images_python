import io
import sys
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter


def process_xObject(xObject):
    for obj in xObject:
        if xObject[obj]["/Subtype"] == "/Image":
            size = (xObject[obj]["/Width"], xObject[obj]["/Height"])

            # White out the image
            white_image = Image.new("RGB", size, "white")
            image = white_image

            # Save the white image as JPEG in memory
            output = io.BytesIO()
            image.save(output, "JPEG")

            # Replace the original image data with the white image data
            xObject[obj]._data = output.getvalue()

        elif xObject[obj]["/Subtype"] == "/Form":
            form_xObject = xObject[obj]["/Resources"]["/XObject"].get_object()
            process_xObject(form_xObject)


def process_page(page):
    xObject = page["/Resources"]["/XObject"].get_object()
    process_xObject(xObject)
    return page


def whiteout_images(input_pdf, output_pdf):
    # Read the input PDF
    reader = PdfReader(input_pdf)

    # Create a PDF writer for the output PDF
    writer = PdfWriter()

    # Process each page and add it to the output PDF
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        if "/XObject" in page["/Resources"].keys():
            processed_page = process_page(page)
        else:
            processed_page = page
        writer.add_page(processed_page)

    # Write the output PDF
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)


if __name__ == "__main__":
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    whiteout_images(input_pdf, output_pdf)

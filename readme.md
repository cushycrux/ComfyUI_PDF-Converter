ComfyUI_PDF-Converter

A simple node for ComfyUI that converts PDF files to PNG images. It can read subfolders and can convert up to 10 pages per second at 150 dpi.

Why does this exist?

Because I needed a simple node for ComfyUI that converts pages of PDF files in PNG images at masses. And it did not exist.


What features does it have?

When the “use_absolute_path” option is enable, the node automatically will read all subfolders in the given folder and will export the images into the given output folder inside ComfyUI’s output folder (default at pdf_extracted_images).

When the “use_absolute_path” option is disabled, the node will read the PDF files from ComfyUI’s input folder or a given subfolder (eg. “PDF” that exists inside the input folder). Leaving the field empty will read PDF’s from the input’s root folder. 

The node will automatically create subdirectories for each PDF file found in the source folder (e.g.  pdf_extracted_images\Testing_PDF)

The output quality (image resolution) can be set by changing the dpi (dots per inch).


What else do I need to know?

The “max_pages_per_pdf” INT input is made to test the environment fast, you probably have to never touch it. 

Since ComfyUI is ignoring nodes without output, the node does not work if no output is connected. This is why the example screenshot and the example workflow are showing the “Preview as Text” node. You could also use a debug node or any other text output node, but it’s needed, otherwise the node will spit out an error.

When the Job is finished it will show you how many pages it has converted on that text output (so it has at least a function).


License

Unlicense - , the node is fully public domain. Do whatever you want with it.
# Brief Overview #
PDFToExcel is a tool that converts (parses) PDF files to nicely formatted Excel tables.  
Its primary use cases are for bank statements and CPF records for bookkeeping purposes.  
**It's only meant for specific files and does not work for all files.**  
For general use cases, please use Excel's "Get Data From PDF" feature or Adobe's "Export PDF to Excel" feature.  
It usually works with varying degrees of success (Excel's "Get Data From PDF" feature works especially well for UOB Bank Statements).  
For unscanned PDF files (i.e. text is not recognised within the file yet), please use Adobe's "Scan and OCR" tool first before using this tool.

### The following files are supported: ###
- OCBC Bank Statement  
- DBS Bank Statement  
- Aspire Bank Statement  
- CPF EzPay Statement  
- CPF Record of Payment (ROP)  

### How to use ###
For it to work, you need 2 files: the exe file "get_data_from_pdf.exe" and the Excel macro template file "template.xltm".  
After opening the template file, a new Excel workbook will be created without modifying the original template file.  
Head over to the developer tab and click "GetDataFromPDF".  
A window should pop up and you may select the files.  
After selecting the files and clicking open, the tables should be appear.  
You may select multiple files of multiple different types (as long they are supported), multiple tables will be created accordingly.  
**Please use a temporary working Excel file for this tool, as data in sheets with the exact same name as the tables might be overwritten.**  
If a table with the same name already exists, then new data will be appended to it.  
Otherwise, a new sheet with the same name as table name will be created, and a new table will be created in the new sheet. 
Below are the mappings:  
- OCBC Bank Statement -> "OCBC"
- DBS Bank Statement -> "DBS"
- Aspire Bank Statement -> "Aspire"
- CPF EzPay Statement -> "CPF EzPay" and "CPF EzPay Summary"
- CPF Record of Payment (ROP) -> "CPF ROP" and "CPF ROP Summary"


### How it works ###
The macro calls and runs the exe file. Processing is done by the exe file behind the scenes.  
The exe file requires an active Excel workbook instance and should not be run directly (except before the first use case).

### Additional Troubleshooting ###
You may need to run the exe file directly once before using the macro to enable your computer to run from an unknown publisher.  
You may get warnings regarding the use of macros, which you can safely ignore.  
During the first use, you may be prompted to select the folder which contains the exe file.  
After selecting, please ensure the exe file remains in the same folder.  
Otherwise, you may be prompted to reselect the folder.  



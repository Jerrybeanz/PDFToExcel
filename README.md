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

### First Time Use ###
For it to work, you need 2 files: the exe file "get_data_from_pdf.exe" and the Excel macro template file "template.xltm".  
After opening the template file, a new Excel macro-enabled workbook will be created without modifying the original template file.  
Note: To enable usage of macros, right click on the Excel file, under "General" tab, "Security" section, "This file came from another computer and might be blocked to help protect this computer." <- Check "Unblock".  
Head over to the developer tab.  
For first time use, please click "PromptForExeFolder" to select the folder containing "get_data_from_pdf.exe".  
In subsequent uses, it will remember this same folder (unless the folder/exe file has been shifted).  
Note: You may also need to run "get_data_from_pdf.exe" directly to enable your computer to run from an unknown publisher.  

### Subsequent Use ###
Head over to the developer tab and click on "GetDataFromPDF".  
A window should pop up and you may select the files.  
After selecting the files and clicking open, the tables should be appear.  
You may select multiple files of multiple different types (as long they are supported), multiple tables will be created accordingly.  
If a table with the same name already exists, then new data will be appended to it.  
Otherwise, a new sheet with the same name as table will be created, and the new table will be created in the new sheet.  
If a sheet with the same name as table so happen to exist, then it will create a new sheet with table name and an index appended to it (e.g. "OCBC 1", "OCBC 2"...)  

Below are the mappings:  
- OCBC Bank Statement -> "OCBC"
- DBS Bank Statement -> "DBS"
- Aspire Bank Statement -> "Aspire"
- CPF EzPay Statement -> "CPF EzPay" and "CPF EzPay Summary"
- CPF Record of Payment (ROP) -> "CPF ROP" and "CPF ROP Summary"

### How it works ###
The macro calls and runs the exe file. Processing is done by the exe file behind the scenes.  
The exe file requires an active Excel workbook instance and should not be run directly (except before the first use case).  
Run it directly will modify the current active Excel workbook instance, which may cause unexpected results.

### Additional Troubleshooting ###
You may get warnings regarding the use of macros, which you can safely ignore.  
If the folder/exe file location ever gets changed, you can manually reselect the exe folder using the "PromptForExeFolder" macro.



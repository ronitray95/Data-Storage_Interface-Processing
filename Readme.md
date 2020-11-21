# SSD37 - Data Storage and Interface for Processing

## Usage

- Install all requirements using:  `pip3 install -r requirements.txt`.
- Add additional requirements as needed in this file.
- Run using `python manage.py runserver`.
- Django will tell the IP and port on which to open the homepage, in the terminal when the above command is run.

## Goals

- Most goals of the project have been met.

1. Taking bibtex file from user.
2. Parsing and storing the bibtex entries into the database.
3. Taking constraints from user such as author name, date range, keywords, etc.
4. Performing inclusion/exclusion according to the constraints.
5. Generating a file for the included bibtex and another file for excluded bibtex with their reasons for exclusion.
6. Downloading the PDF files of the list of included papers.
7. Taking response from user about whether the documents meet their assessment criteria.
8. Storing user responses in database.

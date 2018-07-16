import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("goodreads_library_export.csv")
    reader = csv.reader(f)
    for book_id, title, author, author_lf, additional_authors, isbn, isbn13, my_rating, ave_rating, publisher, binding, number_of_pages, year_published, original_publication_year, date_read, date_added, bookshelves, bookshelves_with_positions, exclusive_shelf, my_review, spoiler, private_notes, read_count, recommended_for, recommended_by, owned_copies, original_purchase_date, original_purchase_location, condition, condition_description, bcid in reader:
        if isbn != "ISBN":
            isbn = isbn.replace("=""", '')
            isbn = isbn.replace('"', '')
            isbn13 = isbn13.replace("=""", '')            
            isbn13 = isbn13.replace('"', '')
            if year_published == '':
                year_published = 0
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year":year_published})
            print(f"Added '{title}' by {author}, {isbn}, {isbn13}, {year_published}")
            db.commit()
            # exit()

if __name__ == "__main__":
    main()

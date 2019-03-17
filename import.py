import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker




#engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgres://iorynocojkwjgc:d6104889e6eeee320700f04b6012980b77506087bded1c13ed5e9d155c97a245@ec2-107-22-162-8.compute-1.amazonaws.com:5432/d22b8flhk40kgi")
db = scoped_session(sessionmaker(bind=engine))

def main():
	f=open('books.csv')
	reader=csv.reader(f)
	for isbn,title,author,year in reader:
		db.execute("INSERT INTO books(isbn,title,author,year)VALUES(:isbn,:title,:author,:year)",
			       {'isbn':isbn,'title':title,'author':author,'year':year})
		print(f'added details {isbn},{title},{author},{year}')
		db.commit()
if __name__=='__main__':
	main()
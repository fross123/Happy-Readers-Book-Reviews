# Project 1

Web Programming with Python and JavaScript

This is a book review website titled Happy-Readers. I will keep it live on Heroku at https://happy-readers.herokuapp.com/.



## application.py

### index()
- Checks if user is logged in. If user is logged in, index.html is rendered and books can be searched. If not, login.html is rendered.

### login()
- Get request will return template 'login.html'
- Post request will allow form to be sumitted.
	- checks if username entered is in database
	- checks password match against 'check_password_hash' function
	- if username and password match, redirects to url_for('index')
	- other issues return error message
	
### signup()
- Get request will render remplate 'signup.html'
- Post request allows form to be submitted
	- accepts user input for First Name, Last Name, Username, and Password.
	- checks if username or password already exist in database
		- if true, user is returned to login screen
	- if not, password is hashed and data is stored in database.
	- return index() which will bring user back to login screen.

### logout()
- removes user from session['user']
- returns index()

### search()
- Get request will return to index() page
- Post request will allow books to be searched
	- search input is taken, escaped with '%' and checked against the database
	- results are checked.
		- if "all" is typed, all results are returned
		- if there are no results, an error message displays.
		- else, results are displayed in books.html
		
### books()
- books.html page is availible wihtout login. However if user clicks a book and is not logged in, they will be sent to login screen.
- returns all books in database

### book(book_id)
- provides details for each book if user is logged in
- includes: book details, reviews submitted, goodreads data.

### review(book_id)
- Post method to allow reviews from users
- book page not found if user is not logged in.
- only allows one review per user.
- returns success page

### errorhandler (404)
- returns 404 error. Can be styled as necessary

### book_api(isbn)
- Returns JSON information on book by isbn.
- url should be as follows:
	- https://happy-readers.herokuapp.com/api/<isbn> with isbn being the isbn of the book you would like information on.
- api access does not require login.



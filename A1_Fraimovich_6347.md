| Function                                                 | Implementation Status | Missing / Bug Found                                                                                                                                                                                                               |
|----------------------------------------------------------|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| add_book_to_catalog                                      | Partial               | bug found: valid inputs return False instead of True, <br/>otherwise it is implemented correctly I think                                                                                                                          |
| return_book_by_patron                                    | not yet implemented   | returns "not yet implemented", and invalid ID & cases where book is not borrowed is <br/>not handled                                                                                                                              |
| borrow_book_by_patron                                    | partially             | basic checks pass,  cases like no copies available & limits reached handled, <br/>but validation logic not fully implemented: as in, tests pass but it's more of a stub                                                           |
| catalog_display or get_all_books                         | partial               | it does return [] of books, display checks pass, <br/>but does not enforce all constraints such as available copies needing to be <= total copies                                                                                 |
| late fee calculation API or  calculate_late_fee_for_book | not implemented       | returns None or placeholder dict, <br/>fee calc logic not implemented                                                                                                                                                             |
| get_patron_status report                                 | not implemented       | returns empty dict, keys for currently borrowed books, <br/>total late fees and borrowing history is not there, just a placeholder as the structure is missing                                                                    |
| search_books_in_catalog & search_books_api               | not implemented       | returns empty list, no logic exists for: partial, <br/>case-insensitive match for title/author, exact match for ISBN. It also depends on the search func which is not implemented. web/ API endpoints exist but aren't functional |
...
My experience in completing the implementation:
-- This was really challenging, but fun in many ways. 
The good news for me was that most of the core functionalities (such as borrowing books and returning, etc) were implemented successfully almost immediately. 
The tricky part after that was the testing, and I discovered that if I borrow more than one copy of the same book under the same patron ID, 
and then try to return said book, it works only the first time, and then after trying to return the second copy, 
it gives an error stating that the patron ID is incorrect. I don't know if I'm explaining this right, but anyway.  
This was the error it gave initially: This book is not currently borrowed by this patron.
So, that was not fun. That meant that something in my new return by patron function was not logicking correctly.
The other problem was that I was set against adding more helper functions or changing the code drastically, so that gave me limited options.
Eventually, I realized that changing this would be a much bigger undertaking, and it would be far too complicated for me to fix this issue without changing certain 
important aspects-- essentially, I was too scared that trying to fix this would lead to bigger issues. Thus, I abandoned it and just focused on ensuring the functions
were implemented correctly and that all requirements would be met. 
I don't know if this was the right decision though to abandon this endeavour...
All in all, the implementation was complete, but as for the return function, I think that it could be still considered partially complete.
Overall, I learned that constraints in changing code structure can really impact debugging and testing. I also gained experience in adjusting test cases to match my implemented functionality.

I'll mention the functions that were fully implemented:
-- calculate_late_fee_for_book
-- search_books_in_catalog
-- get_patron_status_report
What may have issues in the future, but is implemented:
-- return_book_by_patron (explained previously)

Also, I didn't touch the user interface, for fear that I would mess something up critically. 
So, it still says that implementations are in process.

I didn't create any new functions, so I didn't make new test cases. I did, though update the 
test_late_fee_no_active_borrow test case so that it would assert "no active borrow record" instead of "not implemented".



For the next part of this assignment,
I asked Chat to generate test cases. I don't know if using chat instead of other AI models was a good choice, but in this case I just went with the most widely known option.
ChatGPT (GPT-5) Generated test cases: (I had to try several times to get the prompt right with the right amount of info for it to spew out something I could use)

Prompt: I am building a library management system for a class and already have test cases that work, 
but i need to create more that are similar in style. 

def test_late_fee_no_active_borrow():
    """Checks that the function correctly handles a book that is not currently borrowed."""
    result = calculate_late_fee_for_book("123456", 1)
    # The function should return a message about no active borrow
    assert "no active borrow record" in result["status"].lower()

how do I write test cases for each of the following requirements, keeping in mind that these are the functions I have:
add_book_to_catalog, borrow_book_by_patron, return_book_by_patron, calculate_late_fee_for_book, search_books_in_catalog,
get_patron_status_report.

Here is the first requirement:
- the system has to provide a web interface to add new books to the catalog via a form with the following fields:

Title (required, max 200 characters)
Author (required, max 100 characters)
ISBN (required, exactly 13 digits)
Total copies (required, positive integer)
The system shall display success/error messages and redirect to the catalog view after successful addition.

** ONLY USE PYTEST
... and then I sent the rest of the requirements one by one.

RESULTS OF CHATGPT:
Requirement 1:
def test_add_book_success():
    """Checks that a valid book entry is added successfully."""
    result = add_book_to_catalog("Pride and Prejudice", "Jane Austen", "9780141439518", 3)
    assert result["status"] == "Success"
    assert "added to catalog" in result["message"].lower()


def test_add_book_missing_title():
    """Checks that missing title returns an appropriate error."""
    result = add_book_to_catalog("", "George Orwell", "9780451524935", 2)
    assert result["status"] == "Error"
    assert "title is required" in result["message"].lower()


def test_add_book_invalid_isbn_length():
    """Checks that invalid ISBN (not 13 digits) triggers validation error."""
    result = add_book_to_catalog("1984", "George Orwell", "9780451", 2)
    assert result["status"] == "Error"
    assert "isbn must be 13 digits" in result["message"].lower()


def test_add_book_negative_copies():
    """Checks that a negative number of copies is rejected."""
    result = add_book_to_catalog("Moby Dick", "Herman Melville", "9780142437247", -1)
    assert result["status"] == "Error"
    assert "positive integer" in result["message"].lower()

Requirement 2: 
import database
from typing import List, Dict


def test_catalog_returns_list():
    """Catalog should return a list (possibly empty)."""
    books = database.get_all_books()
    assert isinstance(books, list)


def test_catalog_contains_required_fields():
    """Each book should include id, title, author, isbn, total_copies, available_copies."""
    books: List[Dict] = database.get_all_books()
    for book in books:
        assert "id" in book
        assert "title" in book
        assert "author" in book
        assert "isbn" in book
        assert "total_copies" in book
        assert "available_copies" in book

        assert isinstance(book["id"], int)
        assert isinstance(book["title"], str)
        assert isinstance(book["author"], str)
        assert isinstance(book["isbn"], str)
        assert isinstance(book["total_copies"], int)
        assert isinstance(book["available_copies"], int)


def test_catalog_available_copies_not_exceed_total_and_nonnegative():
    """available_copies must be between 0 and total_copies inclusive."""
    books: List[Dict] = database.get_all_books()
    for book in books:
        total = book["total_copies"]
        avail = book["available_copies"]
        assert isinstance(total, int) and isinstance(avail, int)
        assert 0 <= avail <= total


def test_catalog_ordered_by_title_case_insensitive():
    """Catalog is expected to be ordered by title (case-insensitive)."""
    books: List[Dict] = database.get_all_books()
    titles = [b["title"] for b in books]
    # only check ordering when there are at least 2 books
    if len(titles) >= 2:
        assert titles == sorted(titles, key=lambda s: s.lower())


def test_catalog_returns_empty_list_when_no_books(monkeypatch):
    """If the DB has no books, the function should return an empty list (mocked)."""
    monkeypatch.setattr(database, "get_all_books", lambda: [])
    books = database.get_all_books()
    assert books == []

Requirement 3:
def test_borrow_book_success():
    """Checks that a patron can borrow a book when copies are available."""
    result = borrow_book_by_patron("123456", 1)
    assert result["status"] == "Success"
    assert "borrowed successfully" in result["message"].lower()


def test_borrow_book_no_copies_available():
    """Checks that borrowing fails when no copies are available."""
    result = borrow_book_by_patron("123456", 999)  # assume 999 has 0 copies
    assert result["status"] == "Error"
    assert "no copies available" in result["message"].lower()


def test_borrow_book_exceeds_limit():
    """Checks that borrowing fails when patron exceeds max book limit."""
    # assume patron already borrowed 5 books
    result = borrow_book_by_patron("111111", 3)
    assert result["status"] == "Error"
    assert "borrow limit exceeded" in result["message"].lower()

Requirement 4:
def test_return_book_success():
    """Checks that a borrowed book can be returned successfully."""
    result = return_book_by_patron("123456", 1)
    assert result["status"] == "Success"
    assert "returned successfully" in result["message"].lower()


def test_return_book_not_borrowed():
    """Checks that returning a book not currently borrowed shows an error."""
    result = return_book_by_patron("123456", 99)  # assume 99 not borrowed
    assert result["status"] == "Error"
    assert "not currently borrowed" in result["message"].lower()

Requirement 5:
def test_late_fee_correct_calculation():
    """Checks that late fee is calculated correctly for overdue books."""
    result = calculate_late_fee_for_book("123456", 1)
    assert result["status"] == "Success"
    assert isinstance(result["fee"], (float, int))
    assert result["fee"] >= 0


def test_late_fee_no_active_borrow():
    """Checks that fee calculation fails if no active borrow exists."""
    result = calculate_late_fee_for_book("123456", 999)
    assert result["status"] == "Error"
    assert "no active borrow" in result["message"].lower()

Requirement 6:
def test_search_by_title_partial_match():
    """Checks that partial, case-insensitive title search works."""
    results = search_books_in_catalog("harry", "title")
    assert any("harry" in book["title"].lower() for book in results)


def test_search_by_author_partial_match():
    """Checks that partial, case-insensitive author search works."""
    results = search_books_in_catalog("rowling", "author")
    assert all("rowling" in book["author"].lower() for book in results)


def test_search_by_isbn_exact_match():
    """Checks that exact ISBN search returns only the correct book."""
    results = search_books_in_catalog("9780439139601", "isbn")
    assert len(results) == 1
    assert results[0]["isbn"] == "9780439139601"

Requirement 7:
def test_patron_status_report_contains_all_fields():
    """Checks that patron report includes all expected summary fields."""
    report = get_patron_status_report("123456")
    expected_fields = ["books_currently_borrowed", "borrowing_history_summary", "number_of_books_borrowed", "total_late_fees"]
    for field in expected_fields:
        assert field in report


def test_patron_status_report_new_patron_empty():
    """Checks that a new patron’s report has zero fees and empty borrow lists."""
    report = get_patron_status_report("999999")
    assert report["books_currently_borrowed"] == []
    assert report["borrowing_history_summary"] == []
    assert report["total_late_fees"] == 0.0
    assert report["number_of_books_borrowed"] == 0

**My thoughts on AI-generated/ChatGPT tests**
- Firstly, it used monkeypatch which was interesting, maybe I live under a rock but I haven't used it before ever
- Obviously, the test cases were very clean and well documented, which is a given with AI
- I compared AI coverage of requirements to mine and found that it basically covered everything outlined in the requirements. However,
- here are some more thoughts I had:
Specifically, the Add Book requirement testing made by AI was comparable to mine, but my manually made cases used more
descriptive input examples (in other words, AI was more boring). For requirement 2, the display catelog 
requirements, AI probably covered more basis than I did: it did data field validation, ordering, and empty catalog tests.
- Meanwhile, I was less systematic in checking types & field completeness.

The borrow book requirements testing was similar to mine, in that we both had high coverage of the requirements, though mine were more scenario-driven.
The return book requirements were not as thorough as mine, as I covered late return and invalid patron cases more thoroughly.
The late fee API (requirement 5) tests were better by AI because it tested boundary day values, so what happens when a book is 7, 14, 21 days overdue.
The search function testing was better with AI in my opinion because it covered case-insensitive matching and the case where no results were found. My tests were alright as well, but I think AI just did it cleaner.
The patron status (R7) testing were better manually written because I covered borrowed/returned transitions, while AI only focused on 'field presence'.

Overall, I think a mix of AI and manually written testing is good, but I generally agree that humans are best as we know better than AI what we want in the software we develop, if that makes sense.
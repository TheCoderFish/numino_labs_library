# todo
1. add client side form validation from helper basic ones
2. check edge case for borrowing same book twice by same different person
3. check edge case for returning what is already returned
4. uniform error handler class that will keep the responses consistent
5. add e2e loggers with clean and effecient logs clearly distinct like info , debug, error
6. for listing apis add cursor pagination so that we dont flush entire db
7. create a simple class that will create clean helpers for db access and keep all db related functionality in one simple clean reusable class
8. create a a simple business layer logic class which will have reusable validations methods like is book issued, is available, create similar validation classes for other objects and transaction layer. focus is to improve improve maintainability and testability.
9. Implement edit book and edit member functionality, add an edit button in the actions, on edit open overlay with simple dialog. add clear client side validations. on submit make the button do a loader animation. on success close the overlay.
10. implement simple notifications toat throughout the app, create a simple resuable service class for this.
11.Form validations are basic and can be improved by handling whitespace trimming, preventing empty submissions, and adding business-rule checks (e.g., email validation beyond native HTML checks).
12.API integration can be made more maintainable by avoiding hard coded endpoint paths and centralizing them as constants.
13.remove html alert boxes and create components for this.
14.make the table component resuable across books and members and in members borrowed books.
15. fix brokens tests
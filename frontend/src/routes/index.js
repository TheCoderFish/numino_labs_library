import React from 'react';
import Dashboard from '../components/Dashboard';
import BooksList from '../components/BooksList';
import MembersList from '../components/MembersList';
import CreateBook from '../components/CreateBook';
import CreateMember from '../components/CreateMember';
import BorrowBook from '../components/BorrowBook';
import MemberBorrowedBooks from '../components/MemberBorrowedBooks';
import { PATHS } from '../constants/paths';

const routes = [
  { path: PATHS.HOME, element: <Dashboard /> },
  { path: PATHS.BOOKS, element: <BooksList /> },
  { path: PATHS.BOOKS_EDIT, element: <CreateBook /> },
  { path: PATHS.MEMBERS, element: <MembersList /> },
  { path: PATHS.MEMBERS_EDIT, element: <CreateMember /> },
  { path: PATHS.MEMBERS_BORROWED, element: <MemberBorrowedBooks /> },
  { path: PATHS.CREATE_BOOK, element: <CreateBook /> },
  { path: PATHS.CREATE_MEMBER, element: <CreateMember /> },
  { path: PATHS.BORROW_BOOK, element: <BorrowBook /> },
];

export default routes;
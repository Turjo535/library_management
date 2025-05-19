Based on your codebase and models, here is the database design (ER diagram description):

**Entities and Relationships:**

1. **CustomUser**
   - Inherits from Django's `AbstractUser`
   - Fields: id (PK), username, email (unique), password, penalty_points, plus all standard user fields

2. **Author**
   - id (PK)
   - name
   - bio

3. **Category**
   - id (PK)
   - name

4. **Book**
   - id (PK)
   - title
   - description
   - author (FK to Author)
   - category (FK to Category)
   - total_copies
   - available_copies

5. **Borrow**
   - id (PK)
   - user (FK to CustomUser)
   - book (FK to Book)
   - borrow_date
   - due_date
   - return_date (nullable)

**Relationships:**
- A `Book` belongs to one `Author` and one `Category`.
- A `Borrow` record links a `CustomUser` to a `Book` (many-to-many through Borrow, but each Borrow is a single user-book pair).
- `CustomUser` can have many `Borrow` records.
- `Book` can have many `Borrow` records.

**ER Diagram (textual):**

```
CustomUser (1) <--- (M) Borrow (M) ---> (1) Book (M) ---> (1) Author
                                    |
                                    +---> (1) Category
```

**Table summary:**

- **CustomUser**: id, username, email, password, penalty_points, ...
- **Author**: id, name, bio
- **Category**: id, name
- **Book**: id, title, description, author_id, category_id, total_copies, available_copies
- **Borrow**: id, user_id, book_id, borrow_date, due_date, return_date

If you want a graphical ER diagram, let me know and I can describe how to create one using tools like dbdiagram.io or draw.io!
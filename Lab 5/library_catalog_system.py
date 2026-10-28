"""Library catalog management module."""

import hashlib
import secrets

catalog = {
    "B01": {"title": "Clean Code", "copies": 3},
    "B02": {"title": "The Pragmatic Programmer", "copies": 1},
    "B03": {"title": "Design Patterns", "copies": 2},
}


def issue_book(book_id, patron, active_issues=None):
    """Issue a book to a patron."""
    if active_issues is None:
        active_issues = []

    if book_id not in catalog or catalog[book_id]["copies"] <= 0:
        return False

    catalog[book_id]["copies"] -= 1
    active_issues.append(
        f"Issued book {book_id} to patron {patron}"
    )
    return True


def return_book(book_id):
    """Return a book to the catalog."""
    try:
        catalog[book_id]["copies"] += 1
    except KeyError:
        return False
    return True


def check_availability(book_id):
    """Check whether a book is available."""
    if catalog.get(book_id) is None:
        return False

    return catalog[book_id]["copies"] > 0


def calculate_fine(days_overdue):
    """Calculate overdue fine."""
    return days_overdue * 2.0


def generate_patron_hash(patron_id):
    """Generate a hash for a patron identifier."""
    return hashlib.sha256(patron_id.encode()).hexdigest()


def generate_temp_patron_pin():
    """Generate a temporary patron PIN."""
    return secrets.randbelow(9000) + 1000


def export_catalog(filename="catalog_export.txt"):
    """Export catalog data to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(catalog))

    print(f"Catalog backup exported to: {filename}")


def main():
    """Run the library catalog demo."""
    issue_book("B01", "P101")
    return_book("B02")

    print("Is B01 available:", check_availability("B01"))
    print("Fine accrued:", calculate_fine(4))
    print("Patron Hash:", generate_patron_hash("P101"))
    print("Temp PIN:", generate_temp_patron_pin())

    export_catalog()


main()

from dataclasses import dataclass, fields, astuple
import csv
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://mate.academy/"


@dataclass
class Course:
    name: str
    short_description: str
    duration: str


COURSE_FIELDS = [field.name for field in fields(Course)]


def parse_single_course(card: Tag) -> Course | None:
    def _safe_text(node: Tag) -> str:
        return node.get_text(strip=True) if node else ""

    content = card.find("div", class_="ProfessionCard_content__mPiVi")
    if not content:
        return None

    name = _safe_text(
        content.find("h3", class_="ProfessionCard_title__m7uno")
    )
    short_description = _safe_text(
        content.find("p", class_="ProfessionCard_description__K8weo")
    )
    duration = _safe_text(
        content.find("p", class_="ProfessionCard_duration__13PwX")
    )

    if not name or not short_description or not duration:
        return None

    return Course(
        name=name,
        short_description=short_description,
        duration=duration
    )


def get_all_courses() -> list[Course]:
    try:
        response = requests.get(BASE_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
    except requests.HTTPError:
        return []

    cards_container = soup.find(
        "div", class_="ProfessionsListSectionTemplate_cardsWrapper__un6ny"
    )
    if cards_container is None:
        return []
    cards = cards_container.find_all(
        "a", class_="ProfessionCard_cardWrapper__BCg0O"
    )
    cards_result = []
    for card in cards:
        try:
            course = parse_single_course(card)
            cards_result.append(course)
        except Exception:
            continue
    return cards_result


def write_courses_to_csv(courses: list[Course]) -> None:
    with open("courses.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COURSE_FIELDS)
        if courses:
            writer.writerows(astuple(course) for course in courses)


def main() -> None:
    courses = get_all_courses()
    write_courses_to_csv(courses)


if __name__ == "__main__":
    main()

from dataclasses import dataclass, fields, astuple
import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://mate.academy/"


@dataclass
class Course:
    name: str
    short_description: str
    duration: str


COURSE_FIELDS = [field.name for field in fields(Course)]


def parse_single_course(card) -> Course:
    content = card.find("div", class_="ProfessionCard_content__mPiVi")
    return Course(
        name=content.find(
            "h3", class_="ProfessionCard_title__m7uno"
        ).text,
        short_description=content.find(
            "p", class_="ProfessionCard_description__K8weo"
        ).text,
        duration=content.find(
            "p", class_="ProfessionCard_duration__13PwX")
        .text
    )


def get_all_courses() -> list[Course]:
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "lxml")
    cards_container = soup.find(
        "div", class_="ProfessionsListSectionTemplate_cardsWrapper__un6ny"
    )
    cards = cards_container.find_all(
        "a", class_="ProfessionCard_cardWrapper__BCg0O"
    )
    return [parse_single_course(card) for card in cards]


def write_courses_to_csv(courses: list[Course]) -> None:
    with open("courses.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COURSE_FIELDS)
        writer.writerows([astuple(course) for course in courses])


def main():
    courses = get_all_courses()
    write_courses_to_csv(courses)


if __name__ == "__main__":
    main()

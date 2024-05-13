from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from db.db_models import PersonTable, EventTable, EventPersonAssociation
from api_models import Event


class PersonCRUD:
    """
    Person CRUD operations
    """

    @classmethod
    def create(cls, db: Session, person_name: str):
        db_person = PersonTable(id=uuid4(), name=person_name)
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person

    @classmethod
    def read_by_id(cls, db: Session, row_id: UUID):
        # noinspection PyTypeChecker
        return db.query(PersonTable).filter(PersonTable.id == row_id).first()

    @classmethod
    def get_all_persons(cls, db: Session):
        return db.query(PersonTable).all()

    @classmethod
    def delete_by_id(cls, db: Session, row_id: UUID):
        # noinspection PyTypeChecker
        db_person = db.query(PersonTable).filter(PersonTable.id == row_id).first()
        if db_person:
            # noinspection PyTypeChecker
            db.query(PersonTable).filter(PersonTable.id == row_id).delete()
            db.commit()
            return db_person
        return None


class EventCRUD:
    """
    Event CRUD operations
    """

    @classmethod
    def create(
        cls,
        db: Session,
        event: Event,
    ):
        if not event.persons:
            db_event = EventTable(
                id=event.id,
                title=event.title,
                description=event.description,
                time=event.time,
            )
            db.add(db_event)
            db.commit()
            return db_event
        db_event = EventTable(
            id=event.id,
            title=event.title,
            description=event.description,
            time=event.time,
        )
        for person in event.persons:
            # noinspection PyTypeChecker
            new_person = (
                db.query(PersonTable).filter(PersonTable.id == person.id).first()
            )
            if new_person is None:
                return
            new_association = EventPersonAssociation(
                event_id=db_event.id, person_id=new_person.id
            )
            db.add(new_association)

        db.add(db_event)
        db.commit()
        return db_event

    @classmethod
    def add_people_to_event(cls, db: Session, person_ids: list[UUID], event_id: UUID):
        # noinspection PyTypeChecker
        db_event = db.query(EventTable).filter(EventTable.id == event_id).first()
        for person_id in person_ids:
            # noinspection PyTypeChecker
            new_person = (
                db.query(PersonTable).filter(PersonTable.id == person_id).first()
            )
            if new_person is None:
                return
            new_association = EventPersonAssociation(
                event_id=db_event.id, person_id=new_person.id
            )
            db.add(new_association)
        db.add(db_event)
        db.commit()
        return db_event

    @classmethod
    def read_by_id(cls, db: Session, row_id: UUID):
        # noinspection PyTypeChecker
        return db.query(EventTable).filter(EventTable.id == row_id).first()

    @classmethod
    def get_all_events(cls, db: Session):
        return db.query(EventTable).all()

    @classmethod
    def get_events_in_window(cls, db: Session, start_time, end_time):
        # noinspection PyTypeChecker
        return (
            db.query(EventTable)
            .filter(EventTable.time >= start_time, EventTable.time <= end_time)
            .all()
        )

    @classmethod
    def delete_by_id(cls, db: Session, row_id: UUID):
        # noinspection PyTypeChecker
        db_event = db.query(EventTable).filter(EventTable.id == row_id).first()
        if db_event:
            # noinspection PyTypeChecker
            db.query(EventTable).filter(EventTable.id == row_id).delete()
            return db_event
        return None

    @classmethod
    def get_persons_from_event(cls, db: Session, row_id: UUID):
        # noinspection PyTypeChecker
        db_event = db.query(EventTable).filter(EventTable.id == row_id).first()
        if not db_event:
            return None
        return [relation.person for relation in db_event.persons]

    @classmethod
    def update_event(cls, db: Session, event: Event):
        # noinspection PyTypeChecker
        db_event = db.query(EventTable).filter(EventTable.id == event.id).first()
        if db_event:
            db_event.title = event.title
            db_event.description = event.description
            db_event.time = event.time
            db_event.cancelled = event.cancelled
            db.commit()
            return db_event
        return None

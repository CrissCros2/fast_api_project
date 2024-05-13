from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from starlette import status
from sqlalchemy.orm import Session
from datetime import datetime

from api_models import Event
from db.crud import EventCRUD
from db.database import get_db

events = APIRouter()


@events.get("/")
async def get_all_events(db: Session = Depends(get_db)):
    """
    Access the database and get the list of all events
    """
    events_list: list[Event] = []
    db_events = EventCRUD.get_all_events(db)
    for db_event in db_events:
        events_list.append(
            Event(
                id=db_event.id,
                title=db_event.title,
                description=db_event.description,
                time=db_event.time,
                persons=EventCRUD.get_persons_from_event(db, db_event.id),
            )
        )
    return events_list


@events.get("/event_window")
async def get_events_in_window(
    start_time: datetime, end_time: datetime, db: Session = Depends(get_db)
):
    """
    Get all events within a time window
    """
    events_list: list[Event] = []
    db_events = EventCRUD.get_events_in_window(db, start_time, end_time)
    for db_event in db_events:
        events_list.append(
            Event(
                id=db_event.id,
                title=db_event.title,
                description=db_event.description,
                time=db_event.time,
                persons=EventCRUD.get_persons_from_event(db, db_event.id),
            )
        )
    return events_list


@events.post("/", status_code=status.HTTP_201_CREATED, response_model=Event)
async def create_event(event: Event, db: Session = Depends(get_db)):
    """
    Create event in database
    """
    if not event.persons:
        return EventCRUD.create(db, event)
    result = EventCRUD.create(db, event)
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Person not found"},
        )
    return Event(
        id=event.id,
        title=event.title,
        description=event.description,
        time=event.time,
        persons=event.persons,
    )


@events.get("/{event_id}")
async def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """
    Get individual event by event_id
    """
    db_event = EventCRUD.read_by_id(db, event_id)
    if db_event:
        return db_event
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Person not found"},
    )


@events.put("/{event_id}/add_persons", status_code=status.HTTP_200_OK)
async def add_persons_to_event(
    event_id: UUID, person_ids: list[UUID], db: Session = Depends(get_db)
):
    """
    Add people to event by event_id
    """
    db_event = EventCRUD.add_people_to_event(db, person_ids, event_id)
    if db_event:
        return db_event
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Person not found"},
    )


@events.delete("/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(event_id: UUID, db: Session = Depends(get_db)):
    """
    Delete individual event by event_id
    """
    db_event = EventCRUD.delete_by_id(db, event_id)
    if db_event:
        return db_event
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Person not found"},
    )


@events.patch(
    "/{event_id}/cancel", status_code=status.HTTP_200_OK, response_model=Event
)
async def flip_cancel_event(event_id: UUID, db: Session = Depends(get_db)):
    """
    Cancel or un-cancel an event
    """
    db_event = EventCRUD.read_by_id(db, event_id)
    if not db_event:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Event not found"},
        )
    updated_event = Event(
        id=db_event.id,
        title=db_event.title,
        description=db_event.description,
        time=db_event.time,
        persons=db_event.persons,
        cancelled=not db_event.cancelled,
    )
    db_event = EventCRUD.update_event(db, updated_event)
    return db_event


@events.get("/{event_id}/persons", status_code=status.HTTP_200_OK)
async def get_persons_event(event_id: UUID, db: Session = Depends(get_db)):
    """
    Get all persons associated with an event
    """
    db_persons = EventCRUD.get_persons_from_event(db, event_id)
    if not db_persons:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Event not found"},
        )
    return db_persons


@events.patch("/{event_id}", status_code=status.HTTP_200_OK, response_model=Event)
async def update_event(event_id: UUID, event: Event, db: Session = Depends(get_db)):
    """
    Update an event
    """
    updated_event = Event(
        id=event_id,
        title=event.title,
        description=event.description,
        time=event.time,
        persons=event.persons,
        cancelled=event.cancelled,
    )
    db_event = EventCRUD.update_event(db, updated_event)
    if not db_event:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Event not found"},
        )
    return db_event

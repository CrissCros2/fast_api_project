from abc import ABC
from datetime import datetime
from uuid import uuid4, UUID

from fastapi import status

from api_models import Person, Event


class RoutesTest(ABC):
    """
    Base class for route testing so all methods get tested
    """

    not_allowed_responses = {
        status.HTTP_405_METHOD_NOT_ALLOWED,
        status.HTTP_404_NOT_FOUND,
        status.HTTP_406_NOT_ACCEPTABLE,
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    }

    route: str = NotImplemented

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code in self.not_allowed_responses

    def test_post(self, client):
        response = client.post(self.route)
        assert response.status_code in self.not_allowed_responses

    def test_put(self, client):
        response = client.put(self.route)
        assert response.status_code in self.not_allowed_responses

    def test_delete(self, client):
        response = client.delete(self.route)
        assert response.status_code in self.not_allowed_responses

    def test_patch(self, client):
        response = client.patch(self.route)
        assert response.status_code in self.not_allowed_responses


class TestHealth(RoutesTest):
    """
    Test the "/health" route
    """

    route = "/health"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_200_OK
        assert response.json() == {"status": "ok"}


class TestRoot(RoutesTest):
    """
    Test the "/" route redirects to docs
    """

    route = "/"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_200_OK
        assert "/docs" in str(response.url)


class TestPersonsRoot(RoutesTest):
    """
    Test the "/persons/" rout
    """

    route = "/persons/"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_200_OK
        assert response.json()

    def test_post(self, client):
        response = client.post(f"{self.route}?person_name=chris")
        assert response.json()
        assert response.status_code is status.HTTP_201_CREATED


class TestEventsRoot(RoutesTest):
    """
    Test the "/events/" route
    """

    route = "/events/"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.json()
        assert response.status_code is status.HTTP_200_OK

    def test_post(self, client):
        data = {
            "id": uuid4().hex,
            "title": "blah",
            "description": "blah",
            "time": str(datetime.now()),
        }
        response = client.post(self.route, json=data)
        assert response.status_code is status.HTTP_201_CREATED
        event = Event(**response.json())
        assert event.id == UUID(data["id"])
        assert event.title == data["title"]
        assert event.description == data["description"]
        assert str(event.time) == data["time"]
        assert event.persons == []

        data_good = {
            "id": uuid4().hex,
            "title": "blah",
            "description": "blah",
            "persons": [
                {"id": "cb6d5a97-d871-4bac-8fe8-a117ea3fd9de", "name": "Person2"}
            ],
            "time": str(datetime.now()),
        }
        data_bad = {
            "id": uuid4().hex,
            "title": "blah",
            "description": "blah",
            "persons": [
                {"id": "db6d5a97-d871-4bac-8fe8-a117ea3fd9de", "name": "Person2"}
            ],
            "time": str(datetime.now()),
        }
        response_good = client.post(self.route, json=data_good)
        assert response_good.status_code is status.HTTP_201_CREATED
        event = Event(**response_good.json())
        person = Person(**data_good["persons"][0])
        assert event.id == UUID(data_good["id"])
        assert event.title == data_good["title"]
        assert event.description == data_good["description"]
        assert str(event.time) == data_good["time"]
        assert event.persons == [person]
        response_bad = client.post(self.route, json=data_bad)
        assert response_bad.status_code is status.HTTP_404_NOT_FOUND


class TestEventsByIDExists(RoutesTest):
    """
    Test the "/events/{event_id} route
    """

    route = "/events/f531c403-2fb4-4de9-8b4d-848462adb6cc"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_200_OK
        assert response.json()

    def test_delete(self, client):
        response = client.delete(self.route)
        assert response.status_code is status.HTTP_200_OK

    def test_patch(self, client):
        data = {
            "id": "f531c403-2fb4-4de9-8b4d-848462adb6cc",
            "title": "blah",
            "description": "blah",
            "time": str(datetime.now()),
        }
        response = client.patch(self.route, json=data)
        assert response.status_code is status.HTTP_200_OK
        event = Event(**response.json())
        assert event.id == UUID(data["id"])
        assert event.title == data["title"]
        assert event.description == data["description"]
        assert str(event.time) == data["time"]
        assert event.persons == []


class TestAddPeopleToEvent(RoutesTest):
    """
    Test the "/events/{event_id}/add_persons route
    """

    route = "/events/f531c403-2fb4-4de9-8b4d-848462adb6cc/add_persons"

    def test_put(self, client):
        data_good = ["e1a0bcb9-6827-41bf-9888-fbed5dc9e9bb"]
        data_bad = ["e1a0bcb9-6827-41bf-9888-fbed5dc9e9be"]
        response_good = client.put(self.route, json=data_good)
        response_bad = client.put(self.route, json=data_bad)
        assert response_good.status_code is status.HTTP_200_OK
        assert response_bad.status_code is status.HTTP_404_NOT_FOUND


class TestEventsByIDNotExists(RoutesTest):
    """
    Test the "/events/{event_id} route
    """

    route = "/events/f531c403-2fb4-4de9-8b4d-848462adb6ce"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_404_NOT_FOUND

    def test_delete(self, client):
        response = client.delete(self.route)
        assert response.status_code is status.HTTP_404_NOT_FOUND

    def test_patch(self, client):
        data = {
            "id": "f531c403-2fb4-4de9-8b4d-848462adb6cc",
            "title": "blah",
            "description": "blah",
            "time": str(datetime.now()),
        }
        response = client.patch(self.route, json=data)
        assert response.status_code is status.HTTP_404_NOT_FOUND


class TestCancelEventExists(RoutesTest):
    """
    Test "/events/{event_id}/cancel" route
    """

    route = "/events/f531c403-2fb4-4de9-8b4d-848462adb6cc/cancel"

    def test_patch(self, client):
        response = client.patch(self.route)
        assert response.status_code is status.HTTP_200_OK
        event = Event(**response.json())
        assert event.id == UUID("f531c403-2fb4-4de9-8b4d-848462adb6cc")
        assert event.cancelled is True
        response = client.patch(self.route)
        assert response.status_code is status.HTTP_200_OK
        event = Event(**response.json())
        assert event.id == UUID("f531c403-2fb4-4de9-8b4d-848462adb6cc")
        assert event.cancelled is False


class TestCancelEventNoExists(RoutesTest):
    """
    Test "/events/{event_id}/cancel" route
    """

    route = "/events/f531c403-2fb4-4de9-8b4d-848462adb6ce/cancel"

    def test_patch(self, client):
        response = client.patch(self.route)
        assert response.status_code is status.HTTP_404_NOT_FOUND


class TestPersonByIDExists(RoutesTest):

    route = "/persons/e1a0bcb9-6827-41bf-9888-fbed5dc9e9bb"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_200_OK
        person = Person(**response.json())
        assert person.name == "Person1"
        assert person.id == UUID("e1a0bcb9-6827-41bf-9888-fbed5dc9e9bb")

    def test_delete(self, client):
        response = client.delete(self.route)
        assert response.status_code is status.HTTP_200_OK
        person = Person(**response.json())
        assert person.name == "Person1"
        assert person.id == UUID("e1a0bcb9-6827-41bf-9888-fbed5dc9e9bb")


class TestPersonByIDNotExists(RoutesTest):
    route = f"/persons/{uuid4()}"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_404_NOT_FOUND

    def test_delete(self, client):
        response = client.delete(self.route)
        assert response.status_code is status.HTTP_404_NOT_FOUND


class TestGetPersonsEvent(RoutesTest):

    route = "/events/f531c403-2fb4-4de9-8b4d-848462adb6cd/persons"

    def test_get(self, client):
        response_good = client.get(self.route)
        response_bad = client.get(f"/events/{uuid4()}/persons")
        assert response_bad.status_code is status.HTTP_404_NOT_FOUND
        assert response_good.status_code is status.HTTP_200_OK
        assert response_good.json()


class TestGetEventsInWindow(RoutesTest):

    route = f"/events/event_window?start_time={datetime(2024, 5, 12)}&end_time={datetime(2024, 5, 14)}"

    def test_get(self, client):
        response = client.get(self.route)
        assert response.status_code is status.HTTP_200_OK
        assert response.json()
        assert len(response.json()) == 1

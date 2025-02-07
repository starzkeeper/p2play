from dataclasses import asdict

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from backend.application.friendships.interactors.accept_friend_request import FriendshipRequestDTO, AcceptFriendRequest
from backend.application.friendships.interactors.get_friends import GetAllFriends
from backend.application.friendships.interactors.get_sent_friend_requests import GetSentFriendRequests
from backend.application.friendships.interactors.send_friend_request import SendFriendRequest

router_users = APIRouter(route_class=DishkaRoute)


@router_users.post("/add_friend")
async def add_friend(
        data: FriendshipRequestDTO,
        service: FromDishka[SendFriendRequest]
):
    res = await service(data)
    return {'result': 'request sent'}


@router_users.get("/sent_friend_requests")
async def get_sent_friend_requests(
        service: FromDishka[GetSentFriendRequests],
):
    res = await service()
    return {'result': res}


@router_users.post("/accept_friend_request")
async def accept_friend_request(
        data: FriendshipRequestDTO,
        service: FromDishka[AcceptFriendRequest],
):
    res = await service(data)
    return {'result': 'friend request accepted'}


@router_users.get("/friends")
async def get_all_friends(
        service: FromDishka[GetAllFriends],
):
    res = await service()
    return {'result': asdict(res)}

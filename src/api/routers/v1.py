"""
Define routes for our v1 API.
"""
__all__ = ["router"]

from fastapi import APIRouter, HTTPException

from models.base import model_encoder
from models.profile import Profile
from services import get_service
from services.profile import EditAwardRequest, EditProfileRequest, ProfileService

# All API routes defined in this module will have a path prefix of ``/v1``.
# E.g., ``@router.get("/foo/bar")`` adds a route at ``/v1/foo/bar``.
# :see: https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter
router = APIRouter(prefix="/v1", tags=["v1"])


@router.get("/")
def index() -> dict:
    """
    Simple static route, so that we can confirm the server is running.
    """
    return {"message": "Kia ora te ao!"}


@router.get("/profile/{profile_id}")
async def get_profile(profile_id: int) -> dict:
    """
    Retrieves the profile with the specified ID.

    Returns a 404 if no such profile exists.
    """
    profile_service: ProfileService = get_service(ProfileService)

    async with profile_service.session() as session:
        profile: Profile | None = await profile_service.get_by_id(session, profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return model_encoder(profile)


@router.put("/profile/{profile_id}")
async def edit_profile(profile_id: int, body: EditProfileRequest) -> dict:
    """
    Edits the profile with the specified ID, replacing its attributes from the request
    body, and returns the modified profile.

    Returns a 404 if no such profile exists.
    """
    profile_service: ProfileService = get_service(ProfileService)

    async with profile_service.session() as session:
        profile: Profile | None = await profile_service.edit_by_id(
            session, profile_id, body
        )
        await session.commit()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return model_encoder(profile)


@router.post("/profile")
async def create_profile(body: EditProfileRequest) -> dict:
    """
    Adds a profile to the database using the attributes from the response body, and
    returns the new profile data.
    """
    profile_service: ProfileService = get_service(ProfileService)

    async with profile_service.session() as session:
        profile: Profile | None = await profile_service.create(session, body)
        await session.commit()

    return model_encoder(profile)


@router.post("/profile/{profile_id}/award")
async def bestow_award(profile_id: int, body: EditAwardRequest) -> dict:
    """
    Bestows an award upon a profile and returns the updated profile.
    """
    profile_service: ProfileService = get_service(ProfileService)

    async with profile_service.session() as session:
        profile: Profile | None = await profile_service.bestow_award(
            session, profile_id, body
        )
        await session.commit()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return model_encoder(profile)

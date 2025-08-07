from typing import List, Optional

from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    name: str = Field(..., example="Мясная продукция")
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityResponse(ActivityBase):
    id: int
    level: int
    children: List['ActivityResponse'] = []

    class Config:
        from_attributes = True


class BuildingBase(BaseModel):
    address: str = Field(..., example="г. Москва, ул. Ленина 1, офис 3")
    latitude: float = Field(..., example=55.7558)
    longitude: float = Field(..., example=37.6176)


class BuildingCreate(BuildingBase):
    pass


class BuildingResponse(BuildingBase):
    id: int

    class Config:
        from_attributes = True


class PhoneBase(BaseModel):
    number: str = Field(..., example="8-923-666-13-13")


class PhoneCreate(PhoneBase):
    pass


class PhoneResponse(PhoneBase):
    id: int

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str = Field(..., example="ООО Рога и Копыта")
    building_id: int = Field(..., example=1)


class OrganizationCreate(OrganizationBase):
    phone_numbers: List[str] = Field(..., example=["2-222-222", "8-923-666-13-13"])
    activity_ids: List[int] = Field(..., example=[1, 2])


class OrganizationUpdate(OrganizationBase):
    phone_numbers: List[str] = Field(..., example=["3-333-333"])
    activity_ids: List[int] = Field(..., example=[3])


class OrganizationResponse(OrganizationBase):
    id: int
    phones: List[PhoneResponse]
    building: BuildingResponse
    activities: List[ActivityResponse]

    class Config:
        from_attributes = True

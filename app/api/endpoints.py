from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, crud, database

router = APIRouter()

def verify_api_key(api_key: str = Header(...)):
    if api_key != 'secret-key-123':
        raise HTTPException(status_code=403, detail="Invalid API Key")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/buildings/", response_model=List[schemas.BuildingResponse], tags=["Здания"])
def read_buildings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Получить список зданий с пагинацией.

    Args:
        skip (int): Количество пропускаемых записей (для пагинации). По умолчанию 0.
        limit (int): Максимальное количество возвращаемых записей. По умолчанию 100.

    Returns:
        List[BuildingResponse]: Список зданий.
    """
    buildings = crud.get_buildings(db, skip=skip, limit=limit)
    return buildings


@router.get("/organizations/building/{building_id}", response_model=List[schemas.OrganizationResponse], tags=["Поиск"])
def read_organizations_in_building(
    building_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Получить все организации, расположенные в указанном здании.

    Args:
        building_id (int): Идентификатор здания.

    Returns:
        List[OrganizationResponse]: Список организаций в здании.
    """
    orgs = crud.get_organizations_in_building(db, building_id)
    if not orgs:
        raise HTTPException(status_code=404, detail="No organizations found in this building")
    return orgs


@router.get("/organizations/activity/{activity_id}", response_model=List[schemas.OrganizationResponse], tags=["Поиск"])
def read_organizations_by_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Получить все организации по виду деятельности и всем его подвидам (рекурсивно).

    Args:
        activity_id (int): Идентификатор вида деятельности.

    Returns:
        List[OrganizationResponse]: Список организаций, относящихся к указанной деятельности и её подкатегориям.
                                    Пустой список, если деятельность не найдена.
    """
    orgs = crud.get_organizations_by_activity(db, activity_id)
    if not orgs:
        raise HTTPException(status_code=404, detail="No organizations found for this activity")
    return orgs


@router.get("/organizations/radius/", response_model=List[schemas.OrganizationResponse], tags=["Поиск"])
def read_organizations_by_radius(
    lat: float,
    lon: float,
    radius_km: float,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Получить организации, находящиеся в пределах заданного радиуса от точки.

    Args:
        lat (float): Широта центральной точки.
        lon (float): Долгота центральной точки.
        radius_km (float): Радиус поиска в километрах.

    Returns:
        List[OrganizationResponse]: Список организаций в радиусе.
    """
    orgs = crud.get_organizations_by_radius(db, lat, lon, radius_km)
    return orgs


@router.get("/organizations/bbox/", response_model=List[schemas.OrganizationResponse], tags=["Поиск"])
def read_organizations_by_bbox(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Получить организации, находящиеся в заданной прямоугольной области (bounding box).

    Args:
        min_lat (float): Минимальная широта.
        max_lat (float): Максимальная широта.
        min_lon (float): Минимальная долгота.
        max_lon (float): Максимальная долгота.

    Returns:
        List[OrganizationResponse]: Список организаций в области.
    """
    orgs = crud.get_organizations_by_bbox(db, min_lat, max_lat, min_lon, max_lon)
    return orgs


@router.get("/organizations/{org_id}", response_model=schemas.OrganizationResponse, tags=["Организации"])
def read_organization(
    org_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Получить информацию об организации по её идентификатору.

    Args:
        org_id (int): Идентификатор организации.

    Returns:
        OrganizationResponse: Информация об организации.
    """
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/organizations/search/name/", response_model=List[schemas.OrganizationResponse], tags=["Поиск"])
def search_organizations_by_name(
    name: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Найти организации по названию (частичное совпадение, регистронезависимо).

    Args:
        name (str): Строка для поиска в названии.

    Returns:
        List[OrganizationResponse]: Список подходящих организаций.
    """
    orgs = crud.get_organizations_by_name(db, name)
    return orgs


@router.post("/activities/", response_model=schemas.ActivityResponse, tags=["Деятельность"])
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Создать новый вид деятельности.

    Args:
        activity (ActivityCreate): Данные для создания деятельности.

    Returns:
        ActivityResponse: Созданный объект деятельности.
    """
    try:
        return crud.create_activity(db, activity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/buildings/", response_model=schemas.BuildingResponse, tags=["Здания"])
def create_building(
    building: schemas.BuildingCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Создать новое здание.

    Args:
        building (BuildingCreate): Данные для создания здания.

    Returns:
        BuildingResponse: Созданный объект здания.
    """
    return crud.create_building(db, building)


@router.post("/organizations/", response_model=schemas.OrganizationResponse, tags=["Организации"])
def create_organization(
    org: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Создать новую организацию с телефонами и видами деятельности.

    Args:
        org (OrganizationCreate): Данные для создания организации.

    Returns:
        OrganizationResponse: Созданный объект организации.
    """
    return crud.create_organization(db, org)
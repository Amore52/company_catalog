from typing import List, Optional

from geopy.distance import geodesic
from sqlalchemy.orm import Session

from . import models, schemas


def get_building(db: Session, building_id: int) -> Optional[models.Building]:
    """
    Получить здание по ID.

    Args:
        db (Session): Сессия SQLAlchemy.
        building_id (int): Идентификатор здания.

    Returns:
        Optional[models.Building]: Объект здания или None, если не найдено.
    """
    return db.query(models.Building).filter(models.Building.id == building_id).first()


def get_buildings(db: Session, skip: int = 0, limit: int = 100) -> List[models.Building]:
    """
    Получить список зданий с пагинацией.

    Args:
        db (Session): Сессия SQLAlchemy.
        skip (int): Количество пропускаемых записей (для пагинации). По умолчанию 0.
        limit (int): Максимальное количество возвращаемых записей. По умолчанию 100.

    Returns:
        List[models.Building]: Список зданий.
    """
    return db.query(models.Building).offset(skip).limit(limit).all()


def get_organizations_in_building(db: Session, building_id: int) -> List[models.Organization]:
    """
    Получить все организации, расположенные в указанном здании.

    Args:
        db (Session): Сессия SQLAlchemy.
        building_id (int): Идентификатор здания.

    Returns:
        List[models.Organization]: Список организаций в здании.
    """
    return db.query(models.Organization).filter(models.Organization.building_id == building_id).all()


def get_organizations_by_activity(db: Session, activity_id: int) -> List[models.Organization]:
    """
    Получить все организации по виду деятельности и всем его подвидам (рекурсивно).

    Args:
        db (Session): Сессия SQLAlchemy.
        activity_id (int): Идентификатор вида деятельности.

    Returns:
        List[models.Organization]: Список организаций, относящихся к указанной деятельности и её подкатегориям.
                                 Пустой список, если деятельность не найдена.
    """
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        return []

    def get_all_children(act: models.Activity) -> List[models.Activity]:
        """Рекурсивно собирает все подвиды деятельности, включая сам объект."""
        children = db.query(models.Activity).filter(models.Activity.parent_id == act.id).all()
        result: List[models.Activity] = [act]
        for child in children:
            result.extend(get_all_children(child))
        return result

    all_activities = get_all_children(activity)
    activity_ids = [a.id for a in all_activities]

    return (
        db.query(models.Organization)
        .join(models.organization_activity)
        .filter(models.organization_activity.c.activity_id.in_(activity_ids))
        .all()
    )


def get_organizations_by_radius(
        db: Session, lat: float, lon: float, radius_km: float
) -> List[models.Organization]:
    """
    Получить организации, находящиеся в пределах заданного радиуса от точки.

    Args:
        db (Session): Сессия SQLAlchemy.
        lat (float): Широта центральной точки.
        lon (float): Долгота центральной точки.
        radius_km (float): Радиус поиска в километрах.

    Returns:
        List[models.Organization]: Список организаций в радиусе.
    """
    buildings = db.query(models.Building).all()
    target = (lat, lon)
    filtered_building_ids = []

    for b in buildings:
        building_loc = (b.latitude, b.longitude)
        if geodesic(target, building_loc).km <= radius_km:
            filtered_building_ids.append(b.id)

    return (
        db.query(models.Organization)
        .filter(models.Organization.building_id.in_(filtered_building_ids))
        .all()
    )


def get_organizations_by_bbox(
        db: Session,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
) -> List[models.Organization]:
    """
    Получить организации, находящиеся в заданной прямоугольной области (bounding box).

    Args:
        db (Session): Сессия SQLAlchemy.
        min_lat (float): Минимальная широта.
        max_lat (float): Максимальная широта.
        min_lon (float): Минимальная долгота.
        max_lon (float): Максимальная долгота.

    Returns:
        List[models.Organization]: Список организаций в области.
    """
    buildings = (
        db.query(models.Building)
        .filter(
            models.Building.latitude >= min_lat,
            models.Building.latitude <= max_lat,
            models.Building.longitude >= min_lon,
            models.Building.longitude <= max_lon,
        )
        .all()
    )
    building_ids = [b.id for b in buildings]
    return (
        db.query(models.Organization)
        .filter(models.Organization.building_id.in_(building_ids))
        .all()
    )


def get_organization(db: Session, org_id: int) -> Optional[models.Organization]:
    """
    Получить организацию по ID.

    Args:
        db (Session): Сессия SQLAlchemy.
        org_id (int): Идентификатор организации.

    Returns:
        Optional[models.Organization]: Объект организации или None, если не найдена.
    """
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()


def get_organizations_by_name(db: Session, name: str) -> List[models.Organization]:
    """
    Найти организации по названию (частичное совпадение, регистронезависимо).

    Args:
        db (Session): Сессия SQLAlchemy.
        name (str): Строка для поиска в названии.

    Returns:
        List[models.Organization]: Список подходящих организаций.
    """
    return db.query(models.Organization).filter(models.Organization.name.ilike(f"%{name}%")).all()


def create_organization(db: Session, org: schemas.OrganizationCreate) -> models.Organization:
    """
    Создать новую организацию с телефонами и видами деятельности.

    Args:
        db (Session): Сессия SQLAlchemy.
        org (schemas.OrganizationCreate): Данные для создания организации.

    Returns:
        models.Organization: Созданный объект организации.
    """
    db_org = models.Organization(name=org.name, building_id=org.building_id)
    db.add(db_org)
    db.flush()

    for number in org.phone_numbers:
        phone = models.Phone(number=number, organization_id=db_org.id)
        db.add(phone)

    activities = db.query(models.Activity).filter(models.Activity.id.in_(org.activity_ids)).all()
    db_org.activities = activities

    db.commit()
    db.refresh(db_org)
    return db_org


def create_activity(db: Session, activity: schemas.ActivityCreate) -> models.Activity:
    """
    Создать новый вид деятельности с проверкой уровня вложенности (макс. 3 уровня).

    Args:
        db (Session): Сессия SQLAlchemy.
        activity (schemas.ActivityCreate): Данные для создания деятельности.

    Raises:
        ValueError: Если родитель не найден или уровень вложенности превышает 2 (т.е. > 3 уровня).

    Returns:
        models.Activity: Созданный объект деятельности.
    """
    level = 0
    if activity.parent_id:
        parent = db.query(models.Activity).filter(models.Activity.id == activity.parent_id).first()
        if not parent:
            raise ValueError("Parent activity not found")
        level = parent.level + 1
        if level > 2:  # Уровни: 0 (корень), 1, 2 → макс. 3 уровня
            raise ValueError("Maximum nesting level is 3")

    db_activity = models.Activity(name=activity.name, parent_id=activity.parent_id, level=level)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def create_building(db: Session, building: schemas.BuildingCreate) -> models.Building:
    """
    Создать новое здание.

    Args:
        db (Session): Сессия SQLAlchemy.
        building (schemas.BuildingCreate): Данные для создания здания.

    Returns:
        models.Building: Созданный объект здания.
    """
    db_building = models.Building(**building.model_dump())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building

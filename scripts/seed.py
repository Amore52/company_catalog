"""
Скрипт для заполнения базы данных тестовыми данными.
Запускается вручную: python scripts/seed.py
"""
import logging
import sys
from app.database import SessionLocal
from app import crud, schemas, models


logger = logging.getLogger("seed")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def seed_data():
    db = SessionLocal()
    try:
        if db.query(models.Building).count() > 0:
            logger.info("Тестовые данные уже есть в базе. Завершаем.")
            return

        logger.info("Начинаем добавление тестовых данных...")

        b1 = crud.create_building(db, schemas.BuildingCreate(
            address="г. Москва, ул. Ленина 1, офис 3",
            latitude=55.7558,
            longitude=37.6176
        ))
        logger.info(f"Здание добавлено: {b1.address} (ID: {b1.id})")

        b2 = crud.create_building(db, schemas.BuildingCreate(
            address="г. Санкт-Петербург, ул. Блюхера 32/1",
            latitude=59.9343,
            longitude=30.3351
        ))
        logger.info(f"Здание добавлено: {b2.address} (ID: {b2.id})")

        food = crud.create_activity(db, schemas.ActivityCreate(name="Еда"))
        logger.info(f"Деятельность добавлена: {food.name} (ID: {food.id}, уровень: {food.level})")

        meat = crud.create_activity(db, schemas.ActivityCreate(name="Мясная продукция", parent_id=food.id))
        dairy = crud.create_activity(db, schemas.ActivityCreate(name="Молочная продукция", parent_id=food.id))
        logger.info(f"Подвиды деятельности добавлены: '{meat.name}' (ID: {meat.id}), '{dairy.name}' (ID: {dairy.id})")

        cars = crud.create_activity(db, schemas.ActivityCreate(name="Автомобили"))
        light = crud.create_activity(db, schemas.ActivityCreate(name="Легковые", parent_id=cars.id))
        parts = crud.create_activity(db, schemas.ActivityCreate(name="Запчасти", parent_id=light.id))
        logger.info(f"Деятельности по автомобилям добавлены: '{cars.name}', '{light.name}', '{parts.name}'")

        org1 = crud.create_organization(db, schemas.OrganizationCreate(
            name="ООО Рога и Копыта",
            building_id=b1.id,
            phone_numbers=["2-222-222", "8-923-666-13-13"],
            activity_ids=[meat.id, dairy.id]
        ))
        logger.info(f"Организация добавлена: '{org1.name}' (ID: {org1.id})")

        org2 = crud.create_organization(db, schemas.OrganizationCreate(
            name="Автосервис Скорость",
            building_id=b2.id,
            phone_numbers=["3-333-333"],
            activity_ids=[parts.id]
        ))
        logger.info(f"Организация добавлена: '{org2.name}' (ID: {org2.id})")

        logger.info("✅ Все тестовые данные успешно добавлены в базу данных.")

    except Exception as e:
        logger.error(f"❌ Ошибка при добавлении тестовых данных: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
import logging
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.member import Member

logger = logging.getLogger(__name__)

async def seed_members(db: AsyncSession) -> None:
    try:
        # First check if data already exists
        result = await db.execute(select(func.count()).select_from(Member))
        count = result.scalar()
        if count > 0:
            logger.info("Members already seeded, skipping.")
            return

        # Prepare the list of 10 test members
        members_data = [
            {"member_id": "EMP001", "name": "Rajesh Kumar", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP002", "name": "Priya Singh", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP003", "name": "Amit Verma", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP004", "name": "Sneha Reddy", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP005", "name": "Vikram Joshi", "join_date": date(2024, 9, 1)},
            {"member_id": "EMP006", "name": "Kavita Nair", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP007", "name": "Suresh Patil", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP008", "name": "Ravi Menon", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP009", "name": "Anita Desai", "join_date": date(2023, 1, 1)},
            {"member_id": "EMP010", "name": "Deepak Shah", "join_date": date(2023, 1, 1)},
        ]

        members = [
            Member(
                member_id=m["member_id"],
                name=m["name"],
                join_date=m["join_date"],
                annual_limit=50000,
                annual_claims_used=0.0,
                policy_id="PLUM_OPD_2024"
            )
            for m in members_data
        ]

        db.add_all(members)
        await db.commit()
        logger.info("Successfully seeded 10 test members.")
    except Exception as e:
        logger.error(f"Error seeding members: {e}", exc_info=True)
        await db.rollback()
        raise e

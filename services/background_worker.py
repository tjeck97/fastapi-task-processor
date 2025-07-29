import asyncio
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.session import SessionLocal
from models.task import TaskStatus, Task

def start_background_worker():
    asyncio.create_task(worker())

async def worker():
    instance_id = str(uuid.uuid4())
    while True:
        db: Session = SessionLocal()
        try:
            # Atomically select and update one pending task to avoid concurrency issues with other instances
            result = db.execute(text("""
                UPDATE tasks
                SET status = 'processing'
                WHERE id = (
                    SELECT id FROM tasks
                    WHERE status = 'pending'
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                )
                RETURNING id
            """))
            row = result.fetchone()

            if row:
                task_id = row[0]
                task = db.query(Task).get(task_id)
                print(f"[{instance_id}] Processing task {task.id}")

                await asyncio.sleep(7)  # Simulate work

                for conv in task.conversations:
                    conv.archived = True

                task.status = TaskStatus.completed
                db.commit()

                print(f"[{instance_id}] Completed task {task.id}")
            else:
                await asyncio.sleep(2)
        except Exception as e:
            db.rollback()
            print("Worker exception:", e)
        finally:
            db.close()

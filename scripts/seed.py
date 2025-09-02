import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from sqlalchemy import insert

from app.database import SessionLocal
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.models.project import Project
from app.models.task import Task, TaskStatusEnum, TaskPriorityEnum
from app.models.project_member import project_members
from app.models.comment import Comment

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database():
    """
    Seed the database with sample data.
    """
    db = SessionLocal()
    
    try:
        print("Seeding database with sample data...")
        
        # Create organizations
        organizations = []
        org_names = ["TechCorp", "DesignStudio", "MarketingAgency"]
        
        for name in org_names:
            org = Organization(
                id=str(uuid.uuid4()),
                name=name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(org)
            db.flush()  # Flush to get the ID
            organizations.append(org)
            print(f"Created organization: {name}")
        
        # Create admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            name="Admin User",
            email="admin@gmail.com",
            hashed_password=pwd_context.hash("123123123"),
            role=UserRole.admin,
            organization_id=organizations[0].id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.flush()
        print(f"Created admin user: {admin_user.email}")
        
        # Create regular users for each organization
        users = []
        for i, org in enumerate(organizations):
            # Create 2 users per organization
            for j in range(1, 3):
                user = User(
                    id=str(uuid.uuid4()),
                    name=f"User {i+1}-{j}",
                    email=f"user{i+1}_{j}@example.com",
                    hashed_password=pwd_context.hash("password123"),
                    role=UserRole.manager if j == 1 else UserRole.member,
                    organization_id=org.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(user)
                db.flush()
                users.append(user)
                print(f"Created user: {user.email}")
        
        # Create projects for each organization
        projects = []
        for i, org in enumerate(organizations):
            # Create 2 projects per organization
            for j in range(1, 3):
                # Kiểm tra cấu trúc model Project - bỏ creator_id
                project = Project(
                    id=str(uuid.uuid4()),
                    name=f"{org.name} Project {j}",
                    description=f"Sample project {j} for {org.name}",
                    organization_id=org.id,
                    # KHÔNG dùng created_by hoặc creator_id
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(project)
                db.flush()
                projects.append(project)
                print(f"Created project: {project.name}")
                
                # Add project members using the table directly
                # Insert admin as member
                stmt = insert(project_members).values(
                    user_id=admin_user.id,
                    project_id=project.id
                )
                db.execute(stmt)
                
                # Add org's users as members
                org_users = [u for u in users if u.organization_id == org.id]
                for user in org_users:
                    stmt = insert(project_members).values(
                        user_id=user.id,
                        project_id=project.id
                    )
                    db.execute(stmt)
                
                # Create tasks for each project
                priorities = [TaskPriorityEnum.LOW, TaskPriorityEnum.MEDIUM, TaskPriorityEnum.HIGH]
                statuses = [TaskStatusEnum.TODO, TaskStatusEnum.IN_PROGRESS, TaskStatusEnum.DONE]

                tasks = []
                for k in range(1, 4):
                    due_date = datetime.utcnow() + timedelta(days=k*7)
                    
                    # Assign to different users in rotation
                    assignee = org_users[k % len(org_users)] if org_users else admin_user
                    
                    task = Task(
                        id=str(uuid.uuid4()),
                        title=f"Task {k} for {project.name}",
                        description=f"Description for task {k} in project {project.name}",
                        status=statuses[k % len(statuses)],
                        priority=priorities[k % len(priorities)],
                        due_date=due_date,
                        project_id=project.id,
                        assignee_id=assignee.id,
                        creator_id=admin_user.id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(task)
                    db.flush()
                    tasks.append(task)
                    print(f"Created task: {task.title}")
                    
                    # Add comments to each task
                    comment = Comment(
                        id=str(uuid.uuid4()),
                        content=f"This is a comment on {task.title}",
                        task_id=task.id,
                        author_id=admin_user.id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(comment)
                    
                    # Add a second comment from another user if available
                    if org_users:
                        comment2 = Comment(
                            id=str(uuid.uuid4()),
                            content=f"Looking into this task now",
                            task_id=task.id,
                            author_id=org_users[0].id,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(comment2)
        
        # Commit all changes
        db.commit()
        print("Database seeded successfully!")
        return True
    
    except IntegrityError as e:
        db.rollback()
        print(f"Data already exists, skipping: {e}")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = seed_database()
    if success:
        print("Database seeding completed successfully!")
    else:
        print("Database seeding failed.")
        sys.exit(1)
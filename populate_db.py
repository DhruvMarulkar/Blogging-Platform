import asyncio
import traceback
from datetime import UTC, datetime, timedelta
from pathlib import Path

print("Starting script...")

import httpx
from sqlalchemy import delete, select, update

print("Imports 1 done")

import models
from database import AsyncSessionLocal, engine
from image_utils import PROFILE_PICS_DIR

print("Before importing app...")

from main import app

print("App imported successfully")


POPULATE_IMAGES_DIR = Path("populate_images")

USERS = [
    {
        "username": "CoreyMSchafer",
        "email": "CoreyMSchafer@gmail.com",
        "password": "TestPassword1!",
        "image": "corey.png",
    },
    {
        "username": "DefaultDude",
        "email": "TestEmail2@test.com",
        "password": "TestPassword2!",
        # No image - uses default
    },
    {
        "username": "WillowTheCat",
        "email": "TestEmail3@test.com",
        "password": "TestPassword3!",
        "image": "willow.png",
    },
    {
        "username": "FarmDogs",
        "email": "TestEmail4@test.com",
        "password": "TestPassword4!",
        "image": "farmdogs.png",
    },
    {
        "username": "PoppyTheCoder",
        "email": "TestEmail5@test.com",
        "password": "TestPassword5!",
        "image": "poppy.png",
    },
    {
        "username": "GoodBoyBronx",
        "email": "TestEmail6@test.com",
        "password": "TestPassword6!",
        "image": "bronx.png",
    },
]

POSTS = [
    {
        "title": "Why I Love FastAPI",
        "content": "FastAPI has completely changed how I build APIs. The automatic documentation, type hints, and async support make development so much faster. Plus, the performance is incredible!",
    },
    {
        "title": "Corey Schafer Has the Best YouTube Tutorials!",
        "content": "This was written by a viewer and definitely not by me... I mean him. Totally not written by him, but by me... a real viewer. Seriously, check out his channel for amazing Python content.",
    },
    {
        "title": "Async/Await Finally Clicked",
        "content": "I've been struggling with async programming for months, but FastAPI's approach finally made it click. Using 'async def' for endpoints and 'await' for database calls just makes sense.",
    },
    {
        "title": "Schafer? I Barely Know Her!",
        "content": "Is anyone actually reading these blog posts? Do they really need to say anything? I can keep going all day. At least AI can... Claude, keep going, please.",
    },
    {
        "title": "Pydantic Validation is Magic",
        "content": "The way Pydantic handles validation in FastAPI is incredible. Define your model with type hints, and boom - automatic validation, serialization, and documentation. No more writing validation code by hand!",
    },
    {
        "title": "From Flask to FastAPI",
        "content": "I made the switch from Flask to FastAPI last month. The learning curve was minimal, and the benefits are huge. Automatic OpenAPI docs, better performance, and native async support. No regrets!",
    },
    {
        "title": "Some of My Favorite Horror Movies",
        "content": "I love horror movies and practical effects. One of my favorites is 'The Thing'. Hereditary is a great modern one, but most people have seen it. One modern one I really liked that not as many people have seen is 'The Night House'. It's a slow burn but really effective. More psychological than jump-scare based.",
    },
    {
        "title": "Type Hints Changed My Life",
        "content": "I used to think type hints were just extra typing (pun intended). But after using FastAPI, I see how they enable incredible tooling - better autocomplete, automatic validation, and self-documenting code.",
    },
    {
        "title": "The Power of Dependency Injection",
        "content": "FastAPI's dependency injection system is so elegant. Need a database session? Just add it as a parameter. Need the current user? Same thing. It makes the code so clean and testable.",
    },
    {
        "title": "SQLAlchemy 2.0 Is Worth the Upgrade",
        "content": "If you're still using SQLAlchemy 1.x patterns, it's time to upgrade. The new 2.0 style with select() and mapped_column() is much more explicit and works beautifully with async.",
    },
    {
        "title": "Hot Take: Python > JavaScript for APIs",
        "content": "Yes, I said it. For backend APIs, Python with FastAPI beats Node.js. Fight me in the comments. (Just kidding, this blog doesn't have comments... yet.)",
    },
    {
        "title": "Understanding HTTP Status Codes",
        "content": "200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Internal Server Error. Learn these codes - they're how your API communicates with the world. FastAPI makes it easy to return the right ones.",
    },
    {
        "title": "Some of My Favorite Video Games",
        "content": "The one I probably play the most, but not my favorite, is League of Legends... It's a love/hate relationship. If you play, you get it. My favorites are all single-player RPGs. The Elder Scrolls series (Especially Morrowind and Skyrim) were awesome. The Baldur's Gate series took up a lot of my time as a kid, and more recently, the 3rd one was great. Speaking of Baldur's Gate, I love that old isometric style of RPG, so I looked for more modern equivalents and found Pillars of Eternity, which was fantastic. Also both Pathfinder: Kingmaker and Wrath of the Righteous were a lot of fun as well.",
    },
    {
        "title": "JWT Authentication Demystified",
        "content": "JSON Web Tokens seemed scary at first, but they're actually pretty simple. Encode some user data, sign it with a secret, and use it to verify requests. FastAPI + PyJWT makes it straightforward.",
    },
    {
        "title": "Tips for API Design",
        "content": "Use nouns for resources (/users, /posts), HTTP verbs for actions (GET, POST, PUT, DELETE), and return consistent responses. FastAPI's response_model helps enforce this consistency.",
    },
    {
        "title": "Path Parameters vs Query Parameters",
        "content": "Use path parameters for required resource identifiers (/users/123) and query parameters for optional filters (/posts?author=corey&limit=10). FastAPI handles both beautifully with automatic validation.",
    },
    {
        "title": "Error Handling Done Right",
        "content": "Don't just return 500 for everything! Use HTTPException to return meaningful status codes and messages. Your API consumers will thank you when debugging issues.",
    },
    {
        "title": "Why I Switched to UV",
        "content": "UV is blazingly fast for Python package management. Install packages in milliseconds instead of minutes. If you haven't tried it yet, you're missing out!",
    },
    {
        "title": "What About Favorite Books?",
        "content": "I don't read a lot of fiction. The last fiction book I read was 'The Martian' by Andy Weir, which I really enjoyed. But most of my reading is non-fiction. Some of my favorites are 'Meditations' by Marcus Aurelius, 'Conscious' by Annaka Harris, 'How to Die' by Seneca, and 'The Last Lecture' by Randy Pausch. The latest fiction book I'm reading through (and have been for a while) is 'House of Leaves' by Mark Z. Danielewski. It's... different, but awesome.",
    },
    {
        "title": "Testing FastAPI Applications",
        "content": "FastAPI's TestClient makes testing a breeze. Write tests for your endpoints, mock dependencies, and catch bugs before they hit production. Your future self will thank you.",
    },
    {
        "title": "Environment Variables and Security",
        "content": "Never hardcode secrets! Use environment variables and pydantic-settings to keep your API keys, database URLs, and JWT secrets safe. It's Security 101.",
    },
    {
        "title": "CORS: The Bane of Frontend Devs",
        "content": "Getting CORS errors? FastAPI's CORSMiddleware is your friend. Just remember: be specific about allowed origins in production. Don't use '*' unless you really mean it.",
    },
    {
        "title": "Async Database Queries",
        "content": "Blocking database calls in async code? That's a performance killer. Use async drivers like psycopg (for PostgreSQL) or aiosqlite to keep your event loop happy.",
    },
    {
        "title": "The Beauty of Response Models",
        "content": "Response models aren't just for documentation - they filter out sensitive fields automatically. Define what goes out, and Pydantic handles the rest.",
    },
    {
        "title": "Let's Talk Board Games",
        "content": "I love Settlers of Catan. It's a classic for a reason. I'm actually going to make a sword in my woodshop soon that will be my friend group's trophy for the annual Catan champion that we're going to call 'The Katana of Catan'. One thing I've always wanted to do, but never have, is play an in-person Dungeons & Dragons campaign. I've played so many D&D inspired video games, but never the real deal. Hopefully someday...",
    },
    {
        "title": "API Versioning Strategies",
        "content": "APIs evolve. Version them from day one! Whether you use URL prefixes (/v1/users) or headers, plan for change. Breaking changes without versioning breaks trust.",
    },
    {
        "title": "Background Tasks in FastAPI",
        "content": "Don't make users wait for emails to send or files to process. FastAPI's BackgroundTasks lets you return immediately while work continues in the background.",
    },
    {
        "title": "Rate Limiting Your API",
        "content": "Protect your API from abuse with rate limiting. Too many requests? Return 429 Too Many Requests. Your server (and your wallet) will thank you.",
    },
    {
        "title": "Documentation That Writes Itself",
        "content": "Add docstrings to your endpoints and they appear in Swagger UI. Add examples to your Pydantic models and they show up too. Documentation has never been this easy.",
    },
    {
        "title": "WebSockets with FastAPI",
        "content": "REST isn't the only game in town. FastAPI supports WebSockets for real-time communication. Chat apps, live updates, notifications - all possible!",
    },
    {
        "title": "Favorite Hobbies, You Ask?",
        "content": "Woodworking, hands down. I love making things with wood, but I wish I had more time for it. There's something special about making something with your own hands, with materials that are local. A lot of the stuff I've built came from trees that fell on my family's property. My stuff might not always be as good as something you buy in a store, but there's a story and a connection there that makes it better than anything I could buy elsewhere.",
    },
    {
        "title": "Custom Validators in Pydantic",
        "content": "Need validation beyond type checking? Pydantic's field_validator and model_validator decorators let you add custom logic. Validate emails, check password strength, whatever you need.",
    },
    {
        "title": "The ORM vs Raw SQL Debate",
        "content": "ORMs like SQLAlchemy add abstraction but can hide performance issues. Know when to use the ORM and when to drop to raw SQL. Both have their place.",
    },
    {
        "title": "Debugging Async Code",
        "content": "Async bugs can be tricky. Use logging liberally, understand the event loop, and don't mix sync and async without care. asyncio.run() is your entry point.",
    },
    {
        "title": "Containerizing FastAPI Apps",
        "content": "Docker + FastAPI = deployment bliss. Create a Dockerfile, build your image, and deploy anywhere. Consistency across environments is priceless.",
    },
    {
        "title": "Health Check Endpoints",
        "content": "Add a /health endpoint to your API. Load balancers and orchestrators need to know if your service is alive. Return 200 if healthy, details if not. I didn't do this in this tutorial, but there's only so much time in a video!",
    },
    {
        "title": "Hmm... What Else?",
        "content": "I'm running out of ideas for these blog posts. Maybe I should just write about how great FastAPI is... Oh wait, I've already done that multiple times. Well, if you're still reading, thanks for sticking with it! You're awesome.",
    },
    {
        "title": "Pagination: Don't Return Everything",
        "content": "Returning 10,000 records in one response? Please don't. Implement pagination with limit and offset (or better, cursor-based). Your database and clients will be happier.",
    },
    {
        "title": "OpenAPI Schema Customization",
        "content": "FastAPI's auto-generated OpenAPI schema is great, but sometimes you need to customize. Add examples, descriptions, and tags to make your docs shine.",
    },
    {
        "title": "Security Headers Matter",
        "content": "Add security headers to your responses: X-Content-Type-Options, X-Frame-Options, Content-Security-Policy. Small effort, big security improvement.",
    },
    {
        "title": "Caching Strategies",
        "content": "Not every request needs to hit the database. Use caching with Redis or even in-memory for frequently accessed data. Your response times will plummet (in a good way).",
    },
    {
        "title": "GraphQL vs REST",
        "content": "GraphQL is trendy, but REST is battle-tested. Choose based on your needs, not hype. FastAPI excels at REST, but Strawberry brings GraphQL if you need it.",
    },
    {
        "title": "Movie Quotes!",
        "content": "'You wanna know how I did it? This is how I did it, Anton. I never saved anything for the swim back.' - 'Gattaca'. One of my favorite movies of all time. As silly as it sounds, that movie is actually one of the main reasons I decided to pursue an internship at NASA back in college. After that internship, I found I had a craving to learn and do more. It pushed me to take programming more seriously, which eventually led me to where I am today... Which is writing a blog post about FastAPI that's just meant to fill space. TLDR: I watched Gattaca and now I'm writing sample blog posts at 3am on a Saturday for this FastAPI tutorial. And you can too!",
    },
]



async def clear_existing_data() -> None:
    print("Clearing existing data...")

    try:
        if PROFILE_PICS_DIR.exists():
            for file in PROFILE_PICS_DIR.iterdir():
                if file.is_file() and file.name != ".gitkeep":
                    file.unlink()

        async with AsyncSessionLocal() as db:
            await db.execute(delete(models.Post))
            await db.execute(delete(models.User))
            await db.commit()

        print("Existing data cleared")

    except Exception:
        traceback.print_exc()


async def update_post_dates() -> None:
    print("Updating post dates...")

    try:
        now = datetime.now(UTC)

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(models.Post).order_by(models.Post.id)
            )

            posts = result.scalars().all()

            for i, post in enumerate(posts):
                post_date = now - timedelta(days=i)

                await db.execute(
                    update(models.Post)
                    .where(models.Post.id == post.id)
                    .values(date_posted=post_date),
                )

            await db.commit()

        print("Post dates updated")

    except Exception:
        traceback.print_exc()


async def populate() -> None:
    print("Starting population...")

    try:
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://localhost",
        ) as client:

            await clear_existing_data()

            users = []

            print(f"Creating {len(USERS)} users...")

            for user_data in USERS:
                response = await client.post(
                    "/api/users",
                    json={
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "password": user_data["password"],
                    },
                )

                print("User create response:", response.status_code)

                print(response.text)

                response.raise_for_status()

                user = response.json()

                response = await client.post(
                    "/api/users/token",
                    data={
                        "username": user_data["email"],
                        "password": user_data["password"],
                    },
                )

                print("Login response:", response.status_code)

                print(response.text)

                response.raise_for_status()

                token = response.json()["access_token"]

                if image_name := user_data.get("image"):
                    image_path = POPULATE_IMAGES_DIR / image_name

                    if image_path.exists():
                        response = await client.patch(
                            f"/api/users/{user['id']}/picture",
                            files={
                                "file": (
                                    image_name,
                                    image_path.read_bytes(),
                                    "image/png",
                                ),
                            },
                            headers={
                                "Authorization": f"Bearer {token}"
                            },
                        )

                        print("Image upload:", response.status_code)

                        response.raise_for_status()

                users.append(
                    {
                        "id": user["id"],
                        "username": user["username"],
                        "token": token,
                    },
                )

            print(f"Creating {len(POSTS)} posts...")

            for i, post_data in enumerate(POSTS):
                user = users[i % len(users)]

                response = await client.post(
                    "/api/posts",
                    json={
                        "title": post_data["title"],
                        "content": post_data["content"],
                    },
                    headers={
                        "Authorization": f"Bearer {user['token']}"
                    },
                )

                print("Post response:", response.status_code)

                print(response.text)

                response.raise_for_status()

                print(f"Created post: {post_data['title']}")

            await update_post_dates()

        await engine.dispose()

        print("\nDONE!")

    except Exception:
        print("\nERROR:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(populate())
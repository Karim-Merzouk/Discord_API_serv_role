from fastapi import FastAPI
import discord
import asyncio
from discord.ext import commands
from pymongo import MongoClient

TOKEN = "MTM1Mzg1NjY3MTgxNzkyNDY2OA.GATEMq.f5q5tlcollnGNEyn8EjhIqNu45AUkQ4W40Csxk"
GUILD_ID = 569076786907054080  # Replace with your Discord Server ID

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")  # Your startup logic here
    yield
    print("Application shutdown")  # Your shutdown logic here

app = FastAPI(lifespan=lifespan)


# Connect to MongoDB
client = MongoClient("mongodb://offsmrk:WJkVjVpDtYIE6Jla@cluster0-shard-00-00.ttyx9.mongodb.net:27017,cluster0-shard-00-01.ttyx9.mongodb.net:27017,cluster0-shard-00-02.ttyx9.mongodb.net:27017/?replicaSet=atlas-vpi2i4-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0")
db = client["discord"]
collection = db["role_assignments"]

# Run the bot in the background
def run_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(TOKEN))

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(TOKEN))

@app.post("/webhook")
async def webhook(data: dict):
    email = data.get("email")
    role_name = data.get("role")

    if not role_name:
        return {"error": "Role not provided"}

    # Store user data in MongoDB
    collection.insert_one({"email": email, "role": role_name})

    return {"message": f"User registered with role {role_name}"}

@bot.event
async def on_member_join(member):
    # Fetch user's email and role from database
    user_data = collection.find_one({"email": member.email})
    
    if user_data:
        role_name = user_data["role"]
        guild = bot.get_guild(GUILD_ID)
        role = discord.utils.get(guild.roles, name=role_name)

        if role:
            await member.add_roles(role)
            await member.send(f"Welcome! You've been assigned the '{role_name}' role.")
        else:
            await member.send(f"Role '{role_name}' not found. Contact an admin.")

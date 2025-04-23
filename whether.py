import sys
import asyncio
from typing import Dict
import aiohttp

# Correctly handle command-line arguments
sms: bool = sys.argv[2]
your_api_key: str = sys.argv[1]
print('Arg SMS:', sms)
print('Arg YOUR_API_KEY:', your_api_key)


def write_log(data: str) -> bool:
    with open("log.txt", "a") as f:
        f.write(data + "\n")
    return True


def load_user(uid: int) -> Dict[str, str]:
    try:
        with open("users.txt") as f:
            for line in f:
                parts = line.strip().split(",")
                if parts[0] == str(uid):
                    userinfo = {"id": parts[0], "name": parts[1],
                                "email": parts[2], "sms_topic": parts[3]}
                    print('userinfo:', userinfo)
                    return userinfo
    except FileNotFoundError:
        print("The file users.txt does not exist.")
    except Exception as e:
        print(f"An error occurred while loading user: {e}")
    return {}


def log_and_email(user: Dict[str, str], city: str, temp: str, sms: bool) -> str:
    msg = f"{user['name']} in {city} -> {temp}°C"
    write_log(msg)
    print('MSG:', msg)
    if sms:
        content = f"SMS to {user['sms_topic']}: {msg}"
        print('SMS:', content)
        return content
    else:
        content = f"EMAIL to {user['email']}: {msg}"
        print("EMAIL:", content)
        return content


async def fetch_weather(city: str, your_api_key: str) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"http://api.weatherapi.com/v1/current.json?key={your_api_key}&q={city}"
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Error fetching weather data: {resp.status}")
            return await resp.json()


async def process(city: str, user_id: int, sms: bool, your_api_key: str) -> None:
    user = load_user(user_id)
    if not user:
        print("User not found")
        return
    try:
        data = await fetch_weather(city, your_api_key)
        temp = data["current"]["temp_c"]
        await asyncio.to_thread(log_and_email, user, city, str(temp), sms)
    except KeyError as e:
        print(f"Key error: {e}. Check the API response structure.")
    except Exception as e:
        print(f"An error occurred: {e}")


def run(
    city: str,
    user_id: int,
    your_api_key: str
) -> None:
    asyncio.run(process(city, user_id, sms, your_api_key))


run(
    city="Chicago",
    user_id=382,
    your_api_key=your_api_key
)

#to enter rasberry pi, use command ssh scr@192.168.1.128 on scr wifi
import asyncio
from aiohttp import web
from rtcbot import RTCConnection
conn = RTCConnection()  # For this example, we use just one global connection
routes = web.RouteTableDef()



async def cleanup(app=None):
    await conn.close()

app = web.Application()
app.add_routes(routes)
app.on_shutdown.append(cleanup)
web.run_app(app)
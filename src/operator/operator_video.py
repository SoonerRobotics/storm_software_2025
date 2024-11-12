from aiohttp import web
routes = web.RouteTableDef()

from rtcbot import RTCConnection, getRTCBotJS, CVCamera

camera = CVCamera()
# For this example, we use just one global connection
conn = RTCConnection()
conn.video.putSubscription(camera)

# Serve the RTCBot javascript library at /rtcbot.js
@routes.get("/rtcbot.js")
async def rtcbotjs(request):
    return web.Response(content_type="application/javascript", text=getRTCBotJS())

# This sets up the connection
@routes.post("/connect")
async def connect(request):
    clientOffer = await request.json()
    serverResponse = await conn.getLocalDescription(clientOffer)
    return web.json_response(serverResponse)

@routes.get("/")
async def index(request):
    with open("index.html", "r") as f:
        return web.Response(content_type="text/html", text=f.read())

async def cleanup(app=None):
    await conn.close()
    camera.close()

app = web.Application()
app.add_routes(routes)
app.on_shutdown.append(cleanup)
web.run_app(app)
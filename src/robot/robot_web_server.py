from aiohttp import web
routes = web.RouteTableDef()
from rtcbot import RTCConnection, CVCamera, GetterSubscription
from robot_serial import RobotSerial

cam = CVCamera()
conn = RTCConnection()
conn.video.putSubscription(cam)
robot = RobotSerial()
robot.begin()


@GetterSubscription
def robotMessages():
    if robot.operator_sendQueue:
        return robot.operator_sendQueue.pop(0)

@conn.subscribe
def controls(msg):
    print(msg)

@routes.post("/connect")
async def connect(request):
    clientOffer = await request.json()
    serverResponse = await conn.getLocalDescription(clientOffer)
    
    return web.json_response(serverResponse)

async def cleanup(app):
    await conn.close()
    cam.close()

def main():
    app = web.Application()
    app.add_routes(routes)
    app.on_shutdown.append(cleanup)
    web.run_app(app)

if __name__ == "__main__":
    main()
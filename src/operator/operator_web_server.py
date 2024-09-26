from aiohttp import web
routes = web.RouteTableDef()
from rtcbot import RTCConnection, getRTCBotJS, Gamepad
from operator_connection_handler import ConnectionHandler

@routes.get("/rtcbot.js")
async def rtcbotjs(request):
    return web.Response(content_type="application/javascript", text=getRTCBotJS())

@routes.post("/connect")
async def connect(request):
    clientOffer = await request.json()
    conn = ConnectionHandler()
    serverResponse = await conn.getLocalDescription(clientOffer)
    return web.json_response(serverResponse)

async def cleanup(app=None):
    await ConnectionHandler.cleanup()

@routes.get("/")
async def index(request):
    return web.Response(
        content_type="text/html",
        text="""
    <html>
        <head>
            <title>RTCBot: Data Channel</title>
            <script src="/rtcbot.js"></script>
        </head>
        <body style="text-align: center;padding-top: 30px;">
            <h1>Click the Button</h1>
            <button type="button" id="mybutton">Click me!</button>
            <p>
            Open the browser's developer tools to see console messages (CTRL+SHIFT+C)
            </p>
            <script>
                var conn = new rtcbot.RTCConnection();
                conn.video.subscribe(function(stream) {
                    document.querySelector("video").srcObject = stream
                });

                async function connect() {
                    let offer = await conn.getLocalDescription();

                    // POST the information to /connect
                    let response = await fetch("/connect", {
                        method: "POST",
                        cache: "no-cache",
                        body: JSON.stringify(offer)
                    });

                    await conn.setRemoteDescription(await response.json());

                    console.log("Ready!");
                }
                connect();


                var mybutton = document.querySelector("#mybutton");
                mybutton.onclick = function() {
                    conn.put_nowait("Button Clicked!");
                };
            </script>
        </body>
    </html>
    """)

def main():
    app = web.Application()
    app.add_routes(routes)
    app.on_shutdown.append(cleanup)
    web.run_app(app)

if __name__ == "__main__":
    main()
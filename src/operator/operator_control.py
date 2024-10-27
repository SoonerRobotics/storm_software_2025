from aiohttp import web
routes = web.RouteTableDef()

from rtcbot import RTCConnection, getRTCBotJS, PiCamera#CVCamera #CVDisplay 
cam = PiCamera()#yuh
#display = CVDisplay
conn = RTCConnection()
conn.video.putSubscription(cam)#yeah



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
    return web.Response(
        content_type="text/html",
        text=r"""
    <html>
        <head>
            <title>RTCBot: REMOTE CONTROL</title>
            <script src="/rtcbot.js"></script>
        </head>
        <body style="text-align: center;padding-top: 30px;">
            <video autoplay playsinline controls></video> <audio autoplay></audio>
            <p>
            Open the browser's developer tools to see console messages (CTRL+SHIFT+C)
            </p>
            <script>
                var conn = new rtcbot.RTCConnection();

               conn.video.subscribe(function(stream) {
                    document.querySelector("video").srcObject = stream;
                });
                
                
                var kb = new rtcbot.Gamepad();

                async function connect() {

                    #let streams = await navigator.mediaDevices.getUserMedia({audio: false, video: true});
                    #conn.video.putSubscription(streams.getVideoTracks()[0]);
                    #conn.audio.putSubscription(streams.getAudioTracks()[0]);

                    let offer = await conn.getLocalDescription();

                    // POST the information to /connect
                    let response = await fetch("/connect", {
                        method: "POST",
                        cache: "no-cache",
                        body: JSON.stringify(offer)
                    });

                    await conn.setRemoteDescription(await response.json());

                    kb.subscribe(conn.put_nowait);

                    console.log("Ready!");
                }
                connect();

            </script>
        </body>
    </html>
    """)

async def cleanup(app=None):
    await conn.close()
    #display.close()
    cam.close()

app = web.Application()
app.add_routes(routes)
app.on_shutdown.append(cleanup)
web.run_app(app)
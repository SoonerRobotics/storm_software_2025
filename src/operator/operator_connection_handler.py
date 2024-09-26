from rtcbot import RTCConnection, Gamepad

controller = Gamepad

class ConnectionHandler:
    active_connections = []

    def __init__(self):
        self.conn = RTCConnection()
        self.conn.onClose(self.close)

        global controller
        self.controllerSubscription = controller.subscribe()
        self.conn.putSubscription(self.controllerSubscription)

        ConnectionHandler.active_connections.append(self)

    def close(self):
        ConnectionHandler.active_connections.remove(self)

    async def getLocalDescription(self, clientOffer):
        return await self.conn.getLocalDescription(clientOffer)

    @staticmethod
    async def cleanup():
        for c in ConnectionHandler.active_connections[:]:
            await c.conn.close()
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.agent_service import run_agent

router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            user_message = await websocket.receive_text()

            await websocket.send_json({
                "type": "status",
                "content": "Atlas received your message."
            })

            await websocket.send_json({
                "type": "status",
                "content": "Running agent..."
            })

            result = await run_agent(user_message)

            response = result["response"]
            traces = result["traces"]

            await websocket.send_json({
                "type": "traces",
                "content": traces
            })

            words = response.split(" ")

            streamed = ""

            for word in words:
                streamed += word + " "

                await websocket.send_json({
                    "type": "token",
                    "content": word + " "
                })

                await asyncio.sleep(0.03)

            await websocket.send_json({
                "type": "done",
                "content": streamed.strip()
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
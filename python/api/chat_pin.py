from python.helpers.api import ApiHandler, Input, Output, Request, Response
from agent import AgentContext
from python.helpers import persist_chat


class PinChat(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        ctxid = input.get("context", "")
        pinned = input.get("pinned", False)

        if not ctxid:
            return {"error": "Context ID is required"}, 400

        context = AgentContext.get(ctxid)
        if not context:
            return {"error": "Context not found"}, 404

        # Update the pinned status
        context.pinned = pinned
        
        # Save the updated context
        persist_chat.save_tmp_chat(context)

        return {
            "message": "Chat pin status updated successfully.",
            "context": ctxid,
            "pinned": pinned
        }

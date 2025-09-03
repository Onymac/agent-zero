from python.helpers.api import ApiHandler, Input, Output, Request, Response
from agent import AgentContext
from python.helpers import persist_chat


class RenameChat(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        try:
            ctxid = input.get("context", "")
            new_name = input.get("name", "")

            if not ctxid:
                return {"error": "Context ID is required"}, 400
            
            if not new_name.strip():
                return {"error": "Name cannot be empty"}, 400

            context = AgentContext.get(ctxid)
            if not context:
                return {"error": "Context not found"}, 404

            # Try to handle task renaming
            try:
                from python.helpers.task_scheduler import TaskScheduler
                scheduler = TaskScheduler.get()
                task = scheduler.get_task_by_uuid(ctxid)
                
                if task and task.context_id == ctxid:
                    # This is a task, update the task name
                    task.update(name=new_name.strip())
                    await scheduler.save()
                    return {
                        "message": "Task renamed successfully.",
                        "name": new_name.strip()
                    }
            except ImportError:
                # TaskScheduler not available, fall back to context rename
                pass
            except Exception as e:
                print(f"Error updating task: {e}")
                # Fall back to context rename
                pass

            # This is a regular chat or task scheduler failed, update the context name
            context.name = new_name.strip()
            # Persist the change
            persist_chat.save_tmp_chat(context)

            return {
                "message": "Chat renamed successfully.",
                "name": new_name.strip()
            }
        except Exception as e:
            print(f"Error in chat_rename: {e}")
            return {"error": f"Failed to rename: {str(e)}"}, 500
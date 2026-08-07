import json
from pathlib import Path
import aiofiles
from fastapi import FastAPI, HTTPException, Path as pathparam, Request, status
from fastapi.responses import JSONResponse

from schema import PromptCreate, PromptRenderRequest, PromptUpdate

DATAFILE = Path("data.json")

default_prompts = {
    1: {
        "title": "Customer Support Bot",
        "template": "You are a helpful support agent. Reply to {customer_name} regarding their order {order_id}.",
        "targetmodel": "gpt-4",
        "tags": ["support", "e-commerce"],
    }
}

app = FastAPI(title="Prompt Management API", version="1.0.0")



async def load_prompts() -> dict:
    if not DATAFILE.exists():
        await save_prompts(default_prompts)
        return default_prompts.copy()

    async with aiofiles.open(DATAFILE, "r", encoding="utf-8") as f:
        content = await f.read()
        if not content.strip():
            return {}
        data = json.loads(content)  
        
        return {int(k): v for k, v in data.items()}


async def save_prompts(data: dict):
    # Fixed: aiofiles.open instead of aiofiles.write
    async with aiofiles.open(DATAFILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=4))  




@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail, 
            "path": request.url.path,
        },
    )


# --- Routes ---

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Prompt Management API!"}


@app.get("/prompts")
async def get_prompts():
    return await load_prompts()


@app.get("/prompts/{prompt_id}")
async def get_prompts_by_prompt_id(
    prompt_id: int = pathparam(..., gt=0, description="Prompt ID to Fetch")
):
    prompts = await load_prompts()  
    prompt = prompts.get(prompt_id)

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt Not Found"
        )
    return prompt


@app.post("/prompts/{prompt_id}", status_code=status.HTTP_201_CREATED)
async def create_prompt(prompt_id: int, prompt: PromptCreate):
    prompts = await load_prompts()
    
   
    if prompt_id in prompts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt already exists",
        )
        
    prompts[prompt_id] = prompt.model_dump()
    await save_prompts(prompts)
    return prompts[prompt_id]


@app.patch("/prompts/{prompt_id}")
async def update_prompt(prompt_id: int, prompt: PromptUpdate):
    prompts = await load_prompts()
    if prompt_id not in prompts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt Not Found"
        )

    updated_data = prompt.model_dump(exclude_unset=True)
    prompts[prompt_id].update(updated_data)
    
    await save_prompts(prompts)
    return prompts[prompt_id]


@app.delete("/prompts/{prompt_id}")
async def delete_prompt_by_id(prompt_id: int):
    prompts = await load_prompts()
    if prompt_id not in prompts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt Not Found"
        )

    deleted_prompt = prompts.pop(prompt_id)
    await save_prompts(prompts)

    return {"message": "Prompt Deleted", "deleted_prompt": deleted_prompt}


@app.post("/prompts/{prompt_id}/render")  
async def prompt_render(prompt_id: int, request: PromptRenderRequest):
    prompts = await load_prompts()
    prompt = prompts.get(prompt_id)  

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt Not Found"
        )

    raw_template = prompt.get("template", "")

    try:
        rendered_text = raw_template.format(**request.variables)  
        return {"rendered_prompt": rendered_text}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required template variable: {e}",
        )
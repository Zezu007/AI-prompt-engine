import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Path as pathparam, status
from schema import PromptCreate, PromptRenderRequest, PromptUpdate

DATA_FILE = Path("prompts.json")

default_prompts = {
    1: {
        "title": "Customer Support Bot",
        "template": "You are a helpful support agent. Reply to {customer_name} regarding their order {order_id}.",
        "targetmodel": "gpt-4",
        "tags": ["support", "e-commerce"],
    }
}


def load_prompt() -> dict:
    # Fix 1: Added parenthesis to .exists()
    if not DATA_FILE.exists():
        save_prompts(default_prompts)
        return default_prompts

    # Fix 2 & 3: Read file and convert string keys back to integers
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {int(k): v for k, v in data.items()}


def save_prompts(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


prompts = load_prompt()

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to the AI Prompt Management API!"}


@app.get("/prompts")
def get_all_prompts():
    return prompts


@app.get("/prompts/{prompt_id}")
def get_prompt_by_id(
    prompt_id: int = pathparam(..., gt=0, description="The prompt you want:")
):
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompts[prompt_id]


# create
@app.post("/prompts/{prompt_id}", status_code=status.HTTP_201_CREATED)
def prompt_creation(prompt_id: int, prompt: PromptCreate):
    if prompt_id in prompts:
        raise HTTPException(status_code=400, detail="Prompt ID already exist")

    prompts[prompt_id] = prompt.model_dump()
    save_prompts(prompts)
    return prompts[prompt_id]


# update
@app.patch("/prompts/{prompt_id}")
def prompt_update(prompt_id: int, prompt: PromptUpdate):
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt ID does not exist")

    updated_data = prompt.model_dump(exclude_unset=True)

    prompts[prompt_id].update(updated_data)
    save_prompts(prompts)
    return prompts[prompt_id]


@app.delete("/prompts/{prompt_id}")
def prompt_delete(prompt_id: int):
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt ID not Found")

    deleted_prompts = prompts.pop(prompt_id)
    save_prompts(prompts)
    return {"message": "Prompt Delete", "deleted prompt": deleted_prompts}


@app.post("/prompts/{prompt_id}/render")
def prompt_render(prompt_id: int, request: PromptRenderRequest):
    if prompt_id not in prompts:
        raise HTTPException(status_code=404, detail="Prompt Not Found")
    raw_template = prompts[prompt_id]["template"]

    try:
        rendered_text = raw_template.format(**request.variables)
        return {"rendered prompt": rendered_text}

    except KeyError as e:
        raise HTTPException(
            status_code=400, detail=f"Missing required template variable :{e}"
        )
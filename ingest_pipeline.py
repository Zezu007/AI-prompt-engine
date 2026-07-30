import json
from pydantic import BaseModel,Field

class SystemConfig(BaseModel):
    model_name:str=Field(min_length=1)
    temperature:float =Field(default=0.7,description='Temperature for the Core')
    max_tokens:int | None=None

class PromptTestCase(BaseModel):
    test_id:int = Field(gt=0)
    prompt_text:str = Field(min_length=1,max_length=500,description="Prompt written for model response")
    category_tags:list[str]
    system_config:SystemConfig

    created_by: str=Field(default='unknown')
    is_active: bool=Field(default=True)

with open('raw_prompts_dataset.json','r') as rfile:
    rdata=json.load(rfile)
    validated_case=[]
    for i in rdata:
        case=PromptTestCase.model_validate(i)
        validated_case.append(case.model_dump())

with open('Clean_validated_Cases.json','w') as wfile:
    json.dump(validated_case,wfile,indent=4)
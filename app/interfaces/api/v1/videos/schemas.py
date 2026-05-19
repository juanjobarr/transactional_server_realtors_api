from pydantic import BaseModel


class VideoTopicResponse(BaseModel):
    id: str
    icon: str
    label: str
    desc: str


class GenerateScriptResponse(BaseModel):
    script: str
    draft_id: str
    script_version_id: str

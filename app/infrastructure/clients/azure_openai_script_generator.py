import base64
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI

from app.config import settings
from app.domain.ports.script_generator import ScriptGeneratorPort


_SYSTEM_PROMPT = (
    "You are a professional script writer who creates short, engaging video scripts "
    "for real estate agents (realtors). Each script is meant to be spoken to camera "
    "in roughly 30 to 45 seconds. The script must:\n"
    "- match the requested tone exactly\n"
    "- open with a strong hook\n"
    "- be conversational and natural to read aloud\n"
    "- avoid markdown, headings, bullet points, stage directions, or bracketed labels\n"
    "- return plain spoken text only\n"
)


class AzureOpenAIScriptGenerator(ScriptGeneratorPort):
    def __init__(self) -> None:
        self._model = AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            temperature=0.7,
        )

    def generate(
        self,
        *,
        topic_code: str,
        topic_label: str,
        title: Optional[str],
        notes: Optional[str],
        tone: str,
        reference_image_bytes: Optional[bytes] = None,
        reference_image_mime: Optional[str] = None,
    ) -> str:
        user_text = self._build_user_text(
            topic_code=topic_code,
            topic_label=topic_label,
            title=title,
            notes=notes,
            tone=tone,
            has_image=reference_image_bytes is not None,
        )

        human_content: Any
        if reference_image_bytes and reference_image_mime:
            b64 = base64.b64encode(reference_image_bytes).decode("ascii")
            human_content = [
                {"type": "text", "text": user_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{reference_image_mime};base64,{b64}"},
                },
            ]
        else:
            human_content = user_text

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=human_content),
        ]
        response = self._model.invoke(messages)
        text = response.content
        return text if isinstance(text, str) else str(text)

    @staticmethod
    def _build_user_text(
        *,
        topic_code: str,
        topic_label: str,
        title: Optional[str],
        notes: Optional[str],
        tone: str,
        has_image: bool,
    ) -> str:
        parts = [
            f"Topic: {topic_label} (code: {topic_code})",
            f"Tone: {tone}",
        ]
        if title:
            parts.append(f"Title: {title}")
        if notes:
            parts.append(f"Notes: {notes}")
        if has_image:
            parts.append(
                "A reference image is attached. Use it as visual context "
                "(property features, setting, mood) to inform the script."
            )
        parts.append("Write the spoken script now.")
        return "\n".join(parts)

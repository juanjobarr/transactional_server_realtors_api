from dataclasses import dataclass


@dataclass
class VideoTopicResponse:
    id: str
    icon: str
    label: str
    desc: str

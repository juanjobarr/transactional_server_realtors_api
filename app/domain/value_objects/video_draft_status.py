from enum import Enum


class VideoDraftStatus(str, Enum):
    DRAFTED = "drafted"
    SCRIPTED = "scripted"
    GENERATED = "generated"
    FAILED = "failed"

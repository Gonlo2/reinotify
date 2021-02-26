#!/usr/bin/env python3
from dataclasses import dataclass


@dataclass
class InotifyEvent:
    wid: str
    mask: int
    cookie: int
    path: str
    name: str

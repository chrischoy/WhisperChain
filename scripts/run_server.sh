#!/bin/bash
uvicorn src.server.server:app --reload --host 0.0.0.0 --port 8000

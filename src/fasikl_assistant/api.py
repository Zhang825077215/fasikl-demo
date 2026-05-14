from fastapi import FastAPI
from pydantic import BaseModel

from fasikl_assistant.agent import PatientAssistantAgent
from fasikl_assistant.models import AnalyzeRequest, AnalyzeResponse
from fasikl_assistant.sample_data import SAMPLE_MESSAGES

app = FastAPI(title="Fasikl Patient Assistant Demo")
agent = PatientAssistantAgent()


class SampleRunResponse(BaseModel):
    results: list[AnalyzeResponse]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    return agent.analyze(request)


@app.get("/samples")
def samples():
    return {"samples": [item.model_dump() for item in SAMPLE_MESSAGES]}


@app.post("/samples/run", response_model=SampleRunResponse)
def run_samples() -> SampleRunResponse:
    results = [
        agent.analyze(AnalyzeRequest(id=item.id, transcript=item.transcript, session_id=item.id))
        for item in SAMPLE_MESSAGES
    ]
    return SampleRunResponse(results=results)

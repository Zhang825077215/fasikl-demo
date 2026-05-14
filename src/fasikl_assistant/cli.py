import argparse
import json

from fasikl_assistant.agent import PatientAssistantAgent
from fasikl_assistant.models import AnalyzeRequest
from fasikl_assistant.sample_data import SAMPLE_MESSAGES


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the patient assistant demo.")
    parser.add_argument("transcript", nargs="?", help="Patient transcript to analyze.")
    parser.add_argument(
        "--samples",
        action="store_true",
        help="Run the bundled sample transcripts.",
    )
    args = parser.parse_args()

    agent = PatientAssistantAgent()
    if args.samples:
        results = [
            agent.analyze(
                AnalyzeRequest(id=item.id, transcript=item.transcript, session_id=item.id)
            )
            for item in SAMPLE_MESSAGES
        ]
        print(json.dumps([item.model_dump() for item in results], indent=2))
        return

    if not args.transcript:
        parser.error("provide a transcript or pass --samples")

    result = agent.analyze(AnalyzeRequest(transcript=args.transcript))
    print(json.dumps(result.model_dump(), indent=2))

from pydantic import BaseModel


class SampleMessage(BaseModel):
    id: str
    transcript: str


SAMPLE_MESSAGES = [
    SampleMessage(
        id="C001",
        transcript="My device stopped turning on yesterday and I use it every morning.",
    ),
    SampleMessage(
        id="C002",
        transcript="The stimulation feels stronger than usual and uncomfortable.",
    ),
    SampleMessage(
        id="C003",
        transcript="My doctor sent the prescription last week. Did you receive it?",
    ),
    SampleMessage(id="C004", transcript="I cannot log into the portal."),
    SampleMessage(id="C005", transcript="When will my supplies arrive?"),
    SampleMessage(id="C006", transcript="Can I use the device while traveling?"),
    SampleMessage(id="C007", transcript="My skin is red after using the device."),
    SampleMessage(id="C008", transcript="How do I charge the device?"),
    SampleMessage(id="C009", transcript="I changed insurance. What should I do next?"),
    SampleMessage(id="C010", transcript="I missed a few days. Can I restart therapy today?"),
]

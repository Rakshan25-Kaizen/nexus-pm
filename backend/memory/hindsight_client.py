from backend.config import get_settings

settings = get_settings()

try:
    from hindsight_client import Hindsight
    client = Hindsight(base_url=settings.hindsight_base_url, api_key=settings.hindsight_api_key)
except Exception as e:
    print(f"[NEXUS] Warning: Hindsight client not available: {e}")

    class _DummyResult:
        def __init__(self):
            self.results = []
            self.text = ""

    class _DummyBank:
        def create(self, **kwargs):
            pass

    class _DummyClient:
        def __init__(self):
            self.banks = _DummyBank()

        def retain(self, **kwargs):
            pass

        def recall(self, **kwargs):
            return _DummyResult()

        def reflect(self, **kwargs):
            return _DummyResult()

    client = _DummyClient()

BANK_MEETINGS = settings.hindsight_bank_meetings
BANK_MEMBERS = settings.hindsight_bank_members
BANK_TASKS = settings.hindsight_bank_tasks

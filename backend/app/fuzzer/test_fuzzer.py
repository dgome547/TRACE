import asyncio
import os
from .fuzzer import Fuzzer, FuzzerConfig

async def run_test():
    payloads_path = os.path.join(os.path.dirname(__file__), "payloads.txt")

    config = FuzzerConfig(
        target_urls=[
            "http://testphp.vulnweb.com/search.php?test=FUZZ",
            "http://testphp.vulnweb.com/login.php?username=FUZZ&password=FUZZ"
        ],
        payloads_path=payloads_path,
        request_timeout=5.0,
        rate_limit=1.0,
        export_format="json"
    )

    fuzzer = Fuzzer()
    await fuzzer.start_fuzzing(config)

if __name__ == "__main__":
    asyncio.run(run_test())


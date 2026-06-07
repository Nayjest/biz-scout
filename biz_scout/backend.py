import time
from collections.abc import Iterator


_CHUNK_DELAY = 0.02


def _stub_markdown(question: str) -> str:
    """Build a placeholder markdown answer for ``question``."""
    return f"""\
### Re: _{question}_

> ⚠️ **Stub response.** The knowledge base and retrieval pipeline are not wired up yet.

Once BizScout is built, this answer will be grounded in the local knowledge base
collected from public sources. A real response would typically include:

- **Overview** — what the company does, in one paragraph.
- **Key facts** — founding year, headquarters, size, funding.
- **Signals** — recent news, hiring trends, product launches.

```text
source: <document the claim was drawn from>
```

_Ask another question to see another streamed stub answer._
"""


def answer_question(question: str) -> Iterator[str]:
    """Stream a markdown answer to ``question`` as a sequence of chunks.

    Yields markdown fragments (word-by-word) with a small delay so callers such as
    ``st.write_stream`` render a live, typewriter-style response. This is the stable
    interface the rest of the app codes against; only the body changes when the real
    backend lands.
    """
    answer = _stub_markdown(question)
    for token in answer.split(" "):
        yield token + " "
        time.sleep(_CHUNK_DELAY)

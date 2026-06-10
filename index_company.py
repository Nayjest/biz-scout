import sys

import microcore as mc

from biz_scout.core import index
from biz_scout.bootstrap.logging import setup_logging
from biz_scout.bootstrap.perplexity_connection import init_perplexity


setup_logging()
init_perplexity()

mc.configure(
    LLM_API_TYPE=mc.ApiType.NONE,
    EMBEDDING_DB_TYPE=mc.EmbeddingDbType.CHROMA,
    EMBEDDING_DB_HOST="",
    USE_LOGGING="print_stream",
)

company = sys.argv[1] if len(sys.argv) > 1 else "OBRIO"
for out in index(company):
    print(out)
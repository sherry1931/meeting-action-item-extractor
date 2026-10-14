# AI Meeting Action-Item Extractor
Transcript -> clean + segment (speaker, sentence) -> extract (rules or LLM) -> validate -> table with task, owner, deadline, status, confidence.

    pip install -r requirements.txt
    python -m actionitems.evaluate --mode rules      # precision / recall / F1 on data/gold.json
    pytest -q
    streamlit run streamlit_app.py                    # upload-to-results UI
    uvicorn actionitems.api:app --reload              # POST /extract
    # LLM mode: cp .env.example .env, add key, then use --mode llm

Transcript format: optional `# Meeting date: YYYY-MM-DD` header, then `Speaker: sentence` lines (optional `[00:12]` timestamps).

## Validation rules
missing owner (-0.15 confidence) · owner not in meeting · missing deadline · deadline in past (-0.2) · deadline > 1 year · invalid date (e.g. Feb 30) · near-duplicate tasks merged (token Jaccard >= 0.7).

## Evaluation
Greedy task matching (Jaccard >= 0.5), then owner and deadline accuracy on matched items. Add more annotated transcripts to `data/` + `gold.json`, and compare `--mode rules` with `--mode llm`.

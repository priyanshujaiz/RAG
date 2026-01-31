import os
from sqlalchemy.orm import Session
from app.models.job import Job
from app.repositories.ai_run_repository import AIRunRepository
from uuid import UUID
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def handle_ai_run(job: Job, db: Session):
    print(f"[WORKER] Starting AI Execution for Job {job.id}")
    
    ai_run_repo = AIRunRepository(db)

    run_id_str = job.payload.get("run_id") if job.payload else None

    if run_id_str:
        run_id = UUID(run_id_str)
    else:
        run_id = job.target_id
        
    ai_run = ai_run_repo.get_by_id(run_id)
    if not ai_run:
        raise ValueError(f"AI Run {run_id} not found")

    ai_run_repo.mark_running(ai_run)

    try:
        input_data = ai_run.input_payload
        documents = input_data.get("context_documents", [])
        user_params = input_data.get("user_parameters", {})
        question = user_params.get("question", "")

        context_text = ""
        for doc in documents:
            doc_title = doc.get("document_title", "Untitled")
            for chunk in doc.get("chunks", []):
                context_text += f"\n--- Document: {doc_title} ---\n{chunk['text']}\n"

        if not context_text:
            context_text = "No relevant documents found."

        system_prompt = (
            "You are a helpful AI assistant. "
            "Answer the user's question using ONLY the context provided below. "
            "If the answer is not in the context, say 'I cannot answer this based on the documents provided.'"
        )
        
        user_prompt = f"""
            Context:
            {context_text}

            Question:
            {question}
            """

        print(f"[WORKER] Sending request to OpenAI for Run {ai_run.id}...")
        response = client.chat.completions.create(
            model="gpt-4o-mini", # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0 # Deterministic
        )

        answer = response.choices[0].message.content

        ai_run.output_payload = {
            "answer": answer,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
        }
        ai_run_repo.mark_success(ai_run)
        print(f"[WORKER] AI Run {ai_run.id} completed successfully.")

    except Exception as e:
        print(f"[WORKER] AI Run {ai_run.id} failed: {e}")
        ai_run_repo.mark_failed(ai_run, str(e))
        raise e
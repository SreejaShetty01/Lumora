import streamlit as st

class LLMEngine:
    def __init__(self, api_key):
        import google.generativeai as genai
        genai.configure(api_key=api_key)

    def generate_notes(self, transcript):
        """Generate structured lecture notes from transcript. Handles long transcripts via chunking."""
        import google.generativeai as genai
        
        # Determine if transcript is long (>30,000 characters, approx. 30 minutes of speech)
        if len(transcript) < 30000:
            prompt = f"""
            You are an expert academic assistant. Transform the following lecture transcript into high-quality, structured study notes.
            
            Transcript:
            {transcript}
            
            Format the output using Markdown with the following sections:
            1. Executive Summary
            2. Key Concepts & Definitions
            3. Detailed Discussion
            4. Examples & Case Studies
            5. Conclusion
            6. Action Items / Future Research
            
            Make it professional, detailed, and easy to read. Do not return any HTML tags.
            """
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction="You are a helpful study assistant that creates excellent lecture notes."
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=4000, # Large output window
                )
            )
            return response.text
        else:
            # Long lecture: chunk and merge
            # Split transcript into chunks of ~25,000 characters
            chunk_size = 25000
            chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction="You are a helpful study assistant that creates excellent lecture notes."
            )
            
            # Step 1: Generate comprehensive Executive Summary
            summary_prompt = f"""
            You are an expert academic assistant. Generate a comprehensive Executive Summary for the following lecture transcript.
            
            Transcript overview:
            {transcript[:40000]} ... [truncated for overview] ... {transcript[-20000:] if len(transcript) > 60000 else ""}
            
            Make the summary detailed, highlighting the main themes and overall flow.
            """
            summary_response = model.generate_content(
                summary_prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.0, max_output_tokens=2000)
            )
            exec_summary = summary_response.text
            
            # Step 2: Generate detailed discussion and key concepts for each chunk
            chunk_notes = []
            for idx, chunk in enumerate(chunks):
                chunk_prompt = f"""
                You are an expert academic assistant. Generate detailed notes (Key Concepts & Definitions, Detailed Discussion, and Examples & Case Studies) for Section {idx+1} of the lecture transcript.
                
                Section {idx+1} Transcript:
                {chunk}
                
                Format using Markdown:
                ### Section {idx+1}: Detailed Notes & Concepts
                - **Key Concepts in this Section**: [List important terms and definitions]
                - **Detailed Discussion**: [Comprehensive summary of explanations, facts, and details discussed in this section]
                - **Examples/Case Studies**: [List examples, metaphors, or scenarios mentioned]
                """
                chunk_response = model.generate_content(
                    chunk_prompt,
                    generation_config=genai.types.GenerationConfig(temperature=0.0, max_output_tokens=3000)
                )
                chunk_notes.append(chunk_response.text)
            
            # Step 3: Generate Conclusion and Action Items
            conclusion_prompt = f"""
            You are an expert academic assistant. Generate a Conclusion and Action Items / Future Research based on the closing section of the lecture transcript.
            
            Closing Section Transcript:
            {transcript[-20000:]}
            """
            conclusion_response = model.generate_content(
                conclusion_prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.0, max_output_tokens=1500)
            )
            conclusion_text = conclusion_response.text
            
            chunk_notes_str = "\n\n".join(chunk_notes)
            # Merge all sections into a single complete document
            final_notes = f"""# Comprehensive Lecture Notes

## Executive Summary
{exec_summary}

---

## Detailed Notes & Concepts
{chunk_notes_str}

---

## Conclusion & Action Items
{conclusion_text}
"""
            return final_notes

    def generate_quiz(self, transcript):
        """Generate a 5-question multiple choice quiz with answers as JSON."""
        import google.generativeai as genai
        prompt = f"""
        You are an expert academic tutor. Generate a 5-question multiple choice quiz based ONLY on the following lecture transcript.
        
        Transcript:
        {transcript}
        
        You must return a JSON array of 5 questions. Do not include markdown code block formatting or any HTML tags.
        Each question object in the JSON array must follow this exact structure:
        {{
            "question": "The question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "A", // must be one of: "A", "B", "C", "D"
            "explanation": "Explanation of the correct answer"
        }}
        """
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction="You are a helpful study assistant that creates excellent lecture quizzes in structured JSON format."
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )
        return response.text

    def generate_flashcards(self, transcript):
        """Generate key concept flashcards from the lecture transcript as JSON."""
        import google.generativeai as genai
        prompt = f"""
        You are an expert study tutor. Create a list of 5 to 10 key concept flashcards based on the following lecture transcript.
        
        Transcript:
        {transcript}
        
        You must return a JSON array of flashcards. Each object must follow this exact structure:
        {{
            "term": "The concept name, term, or formula",
            "definition": "The explanation or definition of the concept"
        }}
        """
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction="You are a helpful study assistant that creates excellent lecture flashcards in structured JSON format."
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )
        return response.text

    def chat_with_context(self, query, context, history):
        """Chat with the user based on lecture context."""
        import google.generativeai as genai
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction="Answer questions based ONLY on the provided lecture context. If the answer is not in the context, say you don't know."
        )
        
        mapped_history = []
        for msg in history:
            role = 'user' if msg['role'] == 'user' else 'model'
            mapped_history.append({
                'role': role,
                'parts': [msg['content']]
            })
            
        chat = model.start_chat(history=mapped_history)
        response = chat.send_message(
            f"Context: {context}\n\nQuestion: {query}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )
        )
        return response.text
